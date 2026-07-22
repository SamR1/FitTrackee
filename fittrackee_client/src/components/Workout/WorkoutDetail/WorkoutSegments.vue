<template>
  <div id="workout-segments">
    <Card>
      <template #title>{{ $t('workouts.SEGMENT', 2) }}</template>
      <template #content>
        <ul>
          <li
            v-for="(segment, index) in segmentsWithSport"
            :key="segment.segment_id"
          >
            <div class="segment-detail">
              <router-link
                :to="{
                  name: 'WorkoutSegment',
                  params: {
                    workoutId: segment.workout_id,
                    segmentId: segment.segment_id,
                  },
                }"
              >
                <span v-if="segment.is_transition" class="segment-transition">
                  {{ $t('workouts.TRANSITION_CAPITALIZED') }}
                </span>
                <div v-else-if="segment.sport" class="sport-label-img">
                  {{ $t(`sports.${segment.sport.label}.LABEL`) }}
                  <SportImage
                    :sport-label="segment.sport.label"
                    :color="segment.sport.color"
                  />
                </div>
                <span v-else-if="!segment.is_transition">
                  {{ $t('workouts.SEGMENT', 1) }} {{ index + 1 }}
                </span>
              </router-link>
              <span v-if="segment.is_transition" class="segment-transition">
                ({{ $t('workouts.DURATION') }}: {{ segment.duration }})
              </span>
              <template v-else>
                ({{ $t('workouts.DISTANCE') }}:
                <Distance
                  :distance="segment.distance"
                  unitFrom="km"
                  :useImperialUnits="useImperialUnits"
                />, {{ $t('workouts.DURATION') }}: {{ segment.duration }})
              </template>
            </div>
          </li>
        </ul>
      </template>
    </Card>
  </div>
</template>

<script setup lang="ts">
  import { computed, toRefs } from 'vue'

  import useSports from '@/composables/useSports.ts'
  import type { IWorkoutSegment } from '@/types/workouts'

  interface Props {
    segments: IWorkoutSegment[]
    useImperialUnits: boolean
  }
  const props = defineProps<Props>()
  const { segments, useImperialUnits } = toRefs(props)

  const { getObjectSport } = useSports()

  const segmentsWithSport = computed(() =>
    segments.value.map((segment) => ({
      ...segment,
      sport: getObjectSport(segment),
    }))
  )
</script>

<style lang="scss" scoped>
  @use '~@/scss/vars.scss' as *;
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

          .segment-detail {
            display: flex;
            gap: $default-padding * 0.5;
            flex-wrap: wrap;
          }
          .sport-label-img {
            display: flex;
            gap: $default-padding * 0.5;

            .sport-img {
              height: 20px;
              width: 20px;
              margin: 0;
            }
          }
        }
        .segment-transition {
          font-style: italic;
        }
      }
    }
  }
</style>
