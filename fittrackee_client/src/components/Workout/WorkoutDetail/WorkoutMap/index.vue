<template>
  <div id="workout-map">
    <div v-if="workoutData.loading" class="leaflet-container" />
    <div v-else>
      <VFullscreen v-if="workoutData.workout.with_gpx" v-model="isFullscreen">
        <div
          class="leaflet-container"
          :class="{ 'fullscreen-map': isFullscreen }"
        >
          <LMap
            v-if="geoJson.jsonData && center && bounds.length === 2"
            :zoom="13"
            :maxZoom="19"
            :center="center"
            :bounds="bounds"
            :zoomAnimation="false"
            ref="workoutMap"
            @ready="fitBounds(bounds)"
            :use-global-leaflet="false"
            class="map"
            :aria-label="$t('workouts.WORKOUT_MAP')"
          >
            <LControlLayers />
            <LControl
              position="topleft"
              class="map-control"
              tabindex="0"
              role="button"
              :aria-label="$t('workouts.RESET_ZOOM')"
              @click="resetZoom"
            >
              <i class="fa fa-refresh" aria-hidden="true" />
            </LControl>
            <LControl
              position="topleft"
              class="map-control"
              tabindex="0"
              role="button"
              :aria-label="
                $t(`workouts.${isFullscreen ? 'EXIT' : 'VIEW'}_FULLSCREEN`)
              "
              @click="toggleFullscreen"
            >
              <i
                :class="`fa fa-${isFullscreen ? 'compress' : 'arrows-alt'}`"
                aria-hidden="true"
              />
            </LControl>
            <LTileLayer
              :url="`${getApiUrl()}workouts/map_tile/{s}/{z}/{x}/{y}.png`"
              :attribution="appConfig.map_attribution"
              :bounds="bounds"
            />
            <LGeoJson :geojson="geoJson.jsonData" />
            <LMarker
              v-if="markerCoordinates.latitude"
              :lat-lng="[
                markerCoordinates.latitude,
                markerCoordinates.longitude,
              ]"
            />
            <LLayerGroup
              :name="$t('workouts.START_AND_FINISH')"
              layer-type="overlay"
            >
              <CustomMarker
                v-if="startMarkerCoordinates.latitude"
                :markerCoordinates="startMarkerCoordinates"
                :isStart="true"
              />
              <CustomMarker
                v-if="endMarkerCoordinates.latitude"
                :markerCoordinates="endMarkerCoordinates"
                :isStart="false"
              />
            </LLayerGroup>
          </LMap>
        </div>
      </VFullscreen>
      <div v-else class="no-map">{{ $t('workouts.NO_MAP') }}</div>
    </div>
  </div>
</template>

<script setup lang="ts">
  import { gpx } from '@tmcw/togeojson'
  import {
    LControl,
    LControlLayers,
    LGeoJson,
    LLayerGroup,
    LMap,
    LMarker,
    LTileLayer,
  } from '@vue-leaflet/vue-leaflet'
  import { computed, ref, toRefs } from 'vue'
  import type { Ref, ComputedRef } from 'vue'
  import 'leaflet/dist/leaflet.css'

  import CustomMarker from '@/components/Workout/WorkoutDetail/WorkoutMap/CustomMarker.vue'
  import useApp from '@/composables/useApp'
  import type { GeoJSONData } from '@/types/geojson'
  import type {
    ILeafletObject,
    TBounds,
    TCenter,
    TCoordinates,
  } from '@/types/map'
  import type { IWorkoutData } from '@/types/workouts'
  import { getApiUrl } from '@/utils'

  interface Props {
    workoutData: IWorkoutData
    markerCoordinates?: TCoordinates
  }
  const props = withDefaults(defineProps<Props>(), {
    markerCoordinates: () => ({}) as TCoordinates,
  })
  const { workoutData, markerCoordinates } = toRefs(props)

  const { appConfig } = useApp()

  const isFullscreen: Ref<boolean> = ref(false)
  const workoutMap: Ref<ILeafletObject | null> = ref(null)

  const bounds: ComputedRef<TBounds> = computed(() => getBounds())
  const center: ComputedRef<TCenter> = computed(() => getCenter(bounds))
  const geoJson: ComputedRef<GeoJSONData> = computed(() =>
    workoutData.value && workoutData.value.gpx
      ? getGeoJson(workoutData.value.gpx)
      : {}
  )
  const startMarkerCoordinates: ComputedRef<TCoordinates> = computed(() =>
    getCoordinates('first')
  )
  const endMarkerCoordinates: ComputedRef<TCoordinates> = computed(() =>
    getCoordinates('last')
  )

  function getGeoJson(gpxContent: string): GeoJSONData {
    if (!gpxContent || gpxContent !== '') {
      try {
        const jsonData = gpx(
          new DOMParser().parseFromString(gpxContent, 'text/xml')
        )
        return { jsonData }
      } catch (e) {
        console.error('Invalid gpx content')
        return {}
      }
    }
    return {}
  }
  function getCoordinates(position: 'first' | 'last'): TCoordinates {
    const index =
      position === 'first' ? 0 : workoutData.value.chartData.length - 1
    return workoutData.value && workoutData.value.chartData.length > 0
      ? {
          latitude: workoutData.value.chartData[index].latitude,
          longitude: workoutData.value.chartData[index].longitude,
        }
      : { latitude: null, longitude: null }
  }
  function getCenter(bounds: ComputedRef<TBounds>): TCenter {
    return [
      (bounds.value[0][0] + bounds.value[1][0]) / 2,
      (bounds.value[0][1] + bounds.value[1][1]) / 2,
    ]
  }
  function fitBounds(bounds: TBounds): void {
    if (workoutMap.value?.leafletObject) {
      workoutMap.value?.leafletObject.fitBounds(bounds)
    }
  }
  function getBounds(): TBounds {
    return workoutData.value
      ? [
          [
            workoutData.value.workout.bounds[0],
            workoutData.value.workout.bounds[1],
          ],
          [
            workoutData.value.workout.bounds[2],
            workoutData.value.workout.bounds[3],
          ],
        ]
      : []
  }
  function resetZoom(): void {
    workoutMap.value?.leafletObject.fitBounds(getBounds())
  }
  function toggleFullscreen(): void {
    isFullscreen.value = !isFullscreen.value
    if (!isFullscreen.value) {
      setTimeout(() => {
        resetZoom()
      }, 100)
    }
  }
</script>

<style lang="scss" scoped>
  @use '~@/scss/vars.scss' as *;
  #workout-map {
    padding: $default-padding 0;
    .leaflet-container,
    .no-map {
      height: 400px;
      width: 600px;
    }
    .no-map {
      line-height: 400px;
      filter: var(--no-map-filter);
    }
    .leaflet-container {
      .map {
        filter: var(--map-filter);
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
      .leaflet-container {
        width: 100%;
        height: 300px;
      }
      .no-map {
        display: none;
      }
    }
  }
</style>
