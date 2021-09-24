<template>
  <div id="workout-map">
    <div
      class="leaflet-container"
      v-if="geoJson.jsonData && center && bounds.length === 2"
    >
      <LMap
        :zoom="options.zoom"
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
      </LMap>
    </div>
  </div>
</template>

<script lang="ts">
  import { gpx } from '@tmcw/togeojson'
  import { LGeoJson, LMap, LTileLayer } from '@vue-leaflet/vue-leaflet'
  import { ComputedRef, PropType, computed, defineComponent, ref } from 'vue'

  import { ROOT_STORE } from '@/store/constants'
  import { GeoJSONData } from '@/types/geojson'
  import { IWorkoutState } from '@/types/workouts'
  import { useStore } from '@/use/useStore'
  import { getApiUrl } from '@/utils'

  export default defineComponent({
    name: 'WorkoutMap',
    components: {
      LGeoJson,
      LMap,
      LTileLayer,
    },
    props: {
      workout: {
        type: Object as PropType<IWorkoutState>,
      },
    },
    setup(props) {
      const store = useStore()
      const workoutMap = ref<null | {
        leafletObject: { fitBounds: (bounds: number[][]) => null }
      }>(null)
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

      const bounds = computed(() =>
        props.workout
          ? [
              [
                props.workout.workout.bounds[0],
                props.workout.workout.bounds[1],
              ],
              [
                props.workout.workout.bounds[2],
                props.workout.workout.bounds[3],
              ],
            ]
          : []
      )
      const appConfig = computed(
        () => store.getters[ROOT_STORE.GETTERS.APP_CONFIG]
      )

      return {
        appConfig,
        bounds: bounds,
        center: computed(() => getCenter(bounds)),
        geoJson: computed(() =>
          props.workout && props.workout.gpx
            ? getGeoJson(props.workout.gpx)
            : {}
        ),
        options: { zoom: 13 },
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
    .leaflet-container {
      height: 400px;
      width: 600px;
    }

    @media screen and (max-width: $small-limit) {
      .leaflet-container {
        width: 100%;
        height: 300px;
      }
    }
  }
</style>
