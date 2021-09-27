<template>
  <div id="workout-segments">
    <Card :without-title="false">
      <template #title>{{ t('workouts.SEGMENT', 2) }}</template>
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
              >{{ t('workouts.SEGMENT', 1) }} {{ index + 1 }}</router-link
            >
            ({{ t('workouts.DISTANCE') }}: {{ segment.distance }} km,
            {{ t('workouts.DURATION') }}: {{ segment.duration }})
          </li>
        </ul>
      </template>
    </Card>
  </div>
</template>

<script lang="ts">
  import { PropType, defineComponent } from 'vue'
  import { useI18n } from 'vue-i18n'

  import Card from '@/components/Common/Card.vue'
  import { IWorkoutSegment } from '@/types/workouts'

  export default defineComponent({
    name: 'WorkoutSegments',
    components: {
      Card,
    },
    props: {
      segments: {
        type: Object as PropType<IWorkoutSegment[]>,
        required: true,
      },
    },
    setup() {
      const { t } = useI18n()
      return { t }
    },
  })
</script>

<style lang="scss" scoped>
  @import '~@/scss/base';
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
