<template>
  <div id="workout-segments">
    <Card>
      <template #title>{{ $t('workouts.SEGMENT', 2) }}</template>
      <template #content>
        <ul>
          <li v-for="(segment, index) in segments" :key="segment.segment_id">
            <router-link
              :to="{
                name: 'WorkoutSegment',
                params: {
                  workoutId: segment.workout_id,
                  segmentId: index + 1,
                },
              }"
              >{{ $t('workouts.SEGMENT', 1) }} {{ index + 1 }}</router-link
            >
            ({{ $t('workouts.DISTANCE') }}:
            <Distance
              :distance="segment.distance"
              unitFrom="km"
              :useImperialUnits="useImperialUnits"
            />, {{ $t('workouts.DURATION') }}: {{ segment.duration }})
          </li>
        </ul>
      </template>
    </Card>
  </div>
</template>

<script setup lang="ts">
  import { toRefs } from 'vue'

  import type { IWorkoutSegment } from '@/types/workouts'

  interface Props {
    segments: IWorkoutSegment[]
    useImperialUnits: boolean
  }
  const props = defineProps<Props>()
  const { segments, useImperialUnits } = toRefs(props)
</script>

<style lang="scss" scoped>
  @import '~@/scss/vars.scss';
  #workout-segments {
    ::v-deep(.card) {
      .card-title {
        text-transform: capitalize;
      }
      .card-content {
        padding-bottom: 0;
        padding-top: 0;
        a {
          font-weight: bold;
        }
        ul {
          padding: 0 $default-padding;
          list-style: square;
        }
      }
    }
  }
</style>
