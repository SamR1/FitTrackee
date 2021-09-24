<template>
  <div id="workout-map">
    <div
      class="leaflet-container"
      v-if="geoJson.jsonData && center && bounds.length === 2"
    >
      <LMap :zoom="options.zoom" :center="center" :bounds="bounds">
        <LTileLayer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
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
  import { ComputedRef, PropType, computed, defineComponent } from 'vue'

  import { GeoJSONData } from '@/types/geojson'
  import { IWorkoutState } from '@/types/workouts'

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

      return {
        bounds: bounds,
        center: computed(() => getCenter(bounds)),
        geoJson: computed(() =>
          props.workout && props.workout.gpx
            ? getGeoJson(props.workout.gpx)
            : {}
        ),
        options: { zoom: 13 },
      }
    },
  })
</script>

<style lang="scss" scoped>
  @import '~@/scss/base';
  .leaflet-container {
    height: 400px;
    width: 600px;
  }
</style>
