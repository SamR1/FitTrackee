<template>
  <div id="workouts-map">
    <div class="map-loading">
      <div v-if="mapLoading">
        {{ $t('common.DATA_IS_LOADING') }}
        <i class="fa fa-refresh fa-spin fa-fw"></i>
      </div>
    </div>
    <template v-if="globalMap">
      <div id="progress">
        <div id="progress-bar"></div>
      </div>
      <div>
        <span class="total-workouts">
          {{ $t('workouts.TOTAL_WORKOUTS_WITH_LOCATION') }}:
        </span>
        {{ ' ' }}
        <span
          v-if="
            workoutsCollection.features.length > 0 ||
            (userHasWorkouts && !mapLoading)
          "
        >
          {{ workoutsCollection.features.length }}
        </span>
        <template v-if="workoutsCollection.limit_exceeded">
          (<span class="limit-exceeded">
            <i class="fa fa-info-circle" aria-hidden="true" />
            {{ $t('workouts.TOTAL_WORKOUTS_LIMIT_EXCEEDED') }} </span
          >)
        </template>
      </div>
    </template>
    <VFullscreen
      v-if="globalMap || workoutsCollection.features.length > 0"
      v-model="isFullscreen"
    >
      <div
        class="leaflet-container"
        :class="{ 'fullscreen-map': isFullscreen }"
      >
        <LMap
          v-if="center"
          v-model:zoom="zoom"
          :maxZoom="19"
          :center="center"
          :bounds="bounds"
          :zoomAnimation="false"
          :preferCanvas="globalMap"
          @ready="fitBounds(bounds)"
          ref="workoutsMap"
          :use-global-leaflet="true"
          class="map"
          :aria-label="$t('workouts.WORKOUTS_MAP')"
        >
          <LControl
            position="topleft"
            class="map-control"
            tabindex="0"
            role="button"
            :title="$t('workouts.RESET_ZOOM')"
            @click="resetZoom"
            @keydown.enter="resetZoom"
          >
            <i class="fa fa-refresh" aria-hidden="true" />
          </LControl>
          <LControl
            position="topleft"
            class="map-control"
            tabindex="0"
            role="button"
            :title="$t(`workouts.${isFullscreen ? 'EXIT' : 'VIEW'}_FULLSCREEN`)"
            @click="toggleFullscreen"
            @keydown.enter="toggleFullscreen"
          >
            <i
              :class="`fa fa-${isFullscreen ? 'compress' : 'arrows-alt'}`"
              aria-hidden="true"
            />
          </LControl>
          <LTileLayer
            :url="`${getApiUrl()}workouts/map_tile/{s}/{z}/{x}/{y}.png`"
            :attribution="appConfig.map_attribution"
            :maxZoom="19"
          />
          <LGeoJson v-if="displayedWorkout" :geojson="displayedWorkout">
            <WorkoutPopup
              :workout="displayedWorkout.properties"
              :sport="
                getSportLabel(displayedWorkout.properties, translatedSports)
              "
              :color="
                getSportColor(displayedWorkout.properties, translatedSports)
              "
            />
          </LGeoJson>
          <LMarkerClusterGroup
            :chunked-loading="globalMap"
            :chunk-interval="1"
            :chunk-progress="updateProgressBar"
          >
            <CustomWorkoutMarker
              v-for="workout in workoutsCollection.features"
              :sport="getSportLabel(workout.properties, translatedSports)"
              :color="getSportColor(workout.properties, translatedSports)"
              :markerCoordinates="{
                latitude: workout.geometry.coordinates[0][0][1],
                longitude: workout.geometry.coordinates[0][0][0],
              }"
              :key="workout.properties.id"
              @click="displayWorkoutGeoJSON(workout.properties.id)"
            >
              <WorkoutPopup
                :workout="workout.properties"
                :sport="getSportLabel(workout.properties, translatedSports)"
                :color="getSportColor(workout.properties, translatedSports)"
              />
            </CustomWorkoutMarker>
          </LMarkerClusterGroup>
        </LMap>
      </div>
    </VFullscreen>
    <div v-else class="no-map">
      <div v-if="!mapLoading">{{ $t('workouts.NO_WORKOUTS_TO_DISPLAY') }}</div>
    </div>
  </div>
</template>

<script setup lang="ts">
  import {
    LMap,
    LTileLayer,
    LGeoJson,
    LControl,
  } from '@vue-leaflet/vue-leaflet'
  import { type PointExpression, type LatLngBoundsLiteral } from 'leaflet'
  import { computed, ref, onUnmounted, toRefs, watch, onMounted } from 'vue'
  import type { ComputedRef, Ref } from 'vue'
  import { LMarkerClusterGroup } from 'vue-leaflet-markercluster'

  import 'leaflet/dist/leaflet.css'
  import 'vue-leaflet-markercluster/dist/style.css'
  import CustomWorkoutMarker from '@/components/Workouts/CustomWorkoutMarker.vue'
  import WorkoutPopup from '@/components/Workouts/WorkoutPopup.vue'
  import useApp from '@/composables/useApp'
  import { WORKOUTS_STORE } from '@/store/constants.ts'
  import type {
    IWorkoutFeature,
    IWorkoutsFeatureCollection,
  } from '@/types/geojson.ts'
  import type { ILeafletObject } from '@/types/map'
  import type { ITranslatedSport } from '@/types/sports.ts'
  import { useStore } from '@/use/useStore.ts'
  import { getApiUrl } from '@/utils'
  import { getSportColor, getSportLabel } from '@/utils/sports.ts'

  interface Props {
    translatedSports: ITranslatedSport[]
    globalMap?: boolean
    userHasWorkouts?: boolean
  }
  const props = withDefaults(defineProps<Props>(), {
    globalMap: false,
    userHasWorkouts: false,
  })
  const { globalMap, translatedSports, userHasWorkouts } = toRefs(props)

  const store = useStore()

  const { appConfig } = useApp()

  let progress: HTMLElement | null = null
  let progressBar: HTMLElement | null = null
  const isMapReady: Ref<boolean> = ref(false)
  const isFullscreen: Ref<boolean> = ref(false)
  const workoutsMap: Ref<ILeafletObject | null> = ref(null)
  const zoom: Ref<number> = ref(1)
  const displayedWorkoutId: Ref<string | null> = ref(null)

  const mapLoading: ComputedRef<boolean> = computed(
    () => store.getters[WORKOUTS_STORE.GETTERS.MAP_LOADING]
  )
  const workoutsCollection: ComputedRef<IWorkoutsFeatureCollection> = computed(
    () => store.getters[WORKOUTS_STORE.GETTERS.AUTH_USER_WORKOUTS_COLLECTION]
  )
  const bounds: ComputedRef<LatLngBoundsLiteral> = computed(() => getBounds())
  const center: ComputedRef<PointExpression> = computed(() => getCenter(bounds))
  const displayedWorkout: ComputedRef<IWorkoutFeature | undefined> = computed(
    () =>
      workoutsCollection.value.features.find(
        (workout) => workout.properties.id === displayedWorkoutId.value
      )
  )

  function displayWorkoutGeoJSON(workoutId: string) {
    displayedWorkoutId.value = workoutId
  }
  function getBounds(): LatLngBoundsLiteral {
    return workoutsCollection.value.bbox.length > 0
      ? [
          [workoutsCollection.value.bbox[1], workoutsCollection.value.bbox[0]],
          [workoutsCollection.value.bbox[3], workoutsCollection.value.bbox[2]],
        ]
      : []
  }
  function getCenter(
    bounds: ComputedRef<LatLngBoundsLiteral>
  ): PointExpression {
    if (bounds.value.length > 0) {
      return [
        (bounds.value[0][0] + bounds.value[1][0]) / 2,
        (bounds.value[0][1] + bounds.value[1][1]) / 2,
      ]
    }
    return [0, 0]
  }
  function fitBounds(bounds: LatLngBoundsLiteral): void {
    isMapReady.value = true
    if (bounds.length > 0) {
      workoutsMap.value?.leafletObject.fitBounds(bounds)
    }
  }
  function resetZoom(): void {
    const newBounds = getBounds()
    if (newBounds.length > 0) {
      workoutsMap.value?.leafletObject.fitBounds(getBounds())
    }
  }
  function toggleFullscreen(): void {
    isFullscreen.value = !isFullscreen.value
    if (!isFullscreen.value) {
      setTimeout(() => {
        resetZoom()
      }, 100)
    }
  }
  // From https://github.com/Leaflet/Leaflet.markercluster/blob/master/example/marker-clustering-realworld.50000.html
  function updateProgressBar(
    processed: number,
    total: number,
    elapsed: number
  ) {
    if (progress && progressBar) {
      if (elapsed > 0 && total > 0) {
        progress.style.display = 'block'
        progressBar.style.width = Math.round((processed / total) * 100) + '%'
      }
      if (!mapLoading.value && processed === total) {
        progress.style.display = 'none'
      }
    }
  }

  watch(
    () => displayedWorkout.value,
    (newWorkout: IWorkoutFeature | undefined) => {
      if (newWorkout?.properties.bounds) {
        workoutsMap.value?.leafletObject.fitBounds([
          [newWorkout.properties.bounds[0], newWorkout.properties.bounds[1]],
          [newWorkout.properties.bounds[2], newWorkout.properties.bounds[3]],
        ])
      }
    }
  )

  onMounted(() => {
    progress = document.getElementById('progress')
    progressBar = document.getElementById('progress-bar')
  })
  onUnmounted(() =>
    store.commit(WORKOUTS_STORE.MUTATIONS.SET_USER_WORKOUTS_COLLECTION, {
      bbox: [],
      features: [],
      type: 'FeatureCollection',
    })
  )
</script>

<style lang="scss" scoped>
  @use '~@/scss/vars.scss' as *;
  #workouts-map {
    padding: $default-padding 0;
    position: relative;

    #progress {
      position: absolute;
      display: none;
      z-index: 2000;
      left: 50%;
      top: 250px;
      width: 200px;
      height: 20px;
      margin-top: -20px;
      margin-left: -100px;
      background-color: #fff;
      background-color: rgba(255, 255, 255);
      border-radius: 4px;
      padding: 2px;
    }

    #progress-bar {
      width: 0;
      height: 100%;
      background-color: #76a6fc;
      border-radius: 4px;
    }

    .total-workouts {
      font-weight: bold;
    }
    .limit-exceeded {
      font-style: italic;
    }

    .leaflet-container,
    .no-map {
      height: 500px;
      width: 100%;
    }
    .no-map {
      line-height: 550px;
      filter: var(--no-map-filter);
    }
    .map-loading {
      height: 25px;
    }
    .leaflet-container {
      .map,
      ::v-deep(.sport-img) {
        filter: var(--map-filter);
      }
      ::v-deep(.marker-cluster div) {
        filter: var(--map-filter-cluster);
      }
      .map-control {
        background: var(--map-control-bg-color);
        padding: 5px 10px;
        border: 2px solid var(--map-control-border-color);
        border-radius: 3px;
        color: var(--map-control-color);

        &:hover {
          background-color: var(--map-control-hover-bg-color);
        }

        .fa {
          text-align: center;
          min-width: 10px;
        }
      }
    }
    ::v-deep(.fullscreen) {
      display: flex;
      align-items: center;
      z-index: 1000; // partial fix on iOS
      .fullscreen-map {
        height: 100%;
        width: 100%;
      }
    }

    @media screen and (max-width: $small-limit) {
      padding: 0;
      .no-map,
      .leaflet-container {
        height: 300px;
        margin-bottom: $default-margin * 2;
      }
      .no-map {
        line-height: 300px;
      }
    }
  }
</style>
