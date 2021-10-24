<template>
  <div id="workout-map">
    <div v-if="workoutData.loading" class="leaflet-container" />
    <div v-else>
      <div class="leaflet-container" v-if="workoutData.workout.with_gpx">
        <LMap
          v-if="geoJson.jsonData && center && bounds.length === 2"
          :zoom="13"
          :center="center"
          :bounds="bounds"
          ref="workoutMap"
          @ready="fitBounds(bounds)"
        >
          <LTileLayer
            :url="`${getApiUrl()}workouts/map_tile/{s}/{z}/{x}/{y}.png`"
            :attribution="appConfig.map_attribution"
            :bounds="bounds"
          />
          <LGeoJson :geojson="geoJson.jsonData" />
          <LMarker
            v-if="markerCoordinates.latitude"
            :lat-lng="[markerCoordinates.latitude, markerCoordinates.longitude]"
          />
        </LMap>
      </div>
      <div v-else class="no-map">{{ $t('workouts.NO_MAP') }}</div>
    </div>
  </div>
</template>

<script lang="ts">
  import { gpx } from '@tmcw/togeojson'
  import { LGeoJson, LMap, LMarker, LTileLayer } from '@vue-leaflet/vue-leaflet'
  import { ComputedRef, PropType, computed, defineComponent, ref } from 'vue'

  import { ROOT_STORE } from '@/store/constants'
  import { TAppConfig } from '@/types/application'
  import { GeoJSONData } from '@/types/geojson'
  import { IWorkoutData, TCoordinates } from '@/types/workouts'
  import { useStore } from '@/use/useStore'
  import { getApiUrl } from '@/utils'

  export default defineComponent({
    name: 'WorkoutMap',
    components: {
      LGeoJson,
      LMap,
      LMarker,
      LTileLayer,
    },
    props: {
      workoutData: {
        type: Object as PropType<IWorkoutData>,
      },
      markerCoordinates: {
        type: Object as PropType<TCoordinates>,
        required: false,
      },
    },
    setup(props) {
      const store = useStore()

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
      function getCenter(bounds: ComputedRef<number[][]>): number[] {
        return [
          (bounds.value[0][0] + bounds.value[1][0]) / 2,
          (bounds.value[0][1] + bounds.value[1][1]) / 2,
        ]
      }
      function fitBounds(bounds: number[][]) {
        if (workoutMap.value?.leafletObject) {
          workoutMap.value?.leafletObject.fitBounds(bounds)
        }
      }

      const workoutMap = ref<null | {
        leafletObject: { fitBounds: (bounds: number[][]) => null }
      }>(null)
      const bounds = computed(() =>
        props.workoutData
          ? [
              [
                props.workoutData.workout.bounds[0],
                props.workoutData.workout.bounds[1],
              ],
              [
                props.workoutData.workout.bounds[2],
                props.workoutData.workout.bounds[3],
              ],
            ]
          : []
      )
      const appConfig: ComputedRef<TAppConfig> = computed(
        () => store.getters[ROOT_STORE.GETTERS.APP_CONFIG]
      )
      const center = computed(() => getCenter(bounds))
      const geoJson = computed(() =>
        props.workoutData && props.workoutData.gpx
          ? getGeoJson(props.workoutData.gpx)
          : {}
      )

      return {
        appConfig,
        bounds,
        center,
        geoJson,
        workoutMap,
        fitBounds,
        getApiUrl,
      }
    },
  })
</script>

<style lang="scss" scoped>
  @import '~@/scss/base';
  #workout-map {
    padding: $default-padding 0;
    .leaflet-container,
    .no-map {
      height: 400px;
      width: 600px;
    }
    .no-map {
      line-height: 400px;
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
