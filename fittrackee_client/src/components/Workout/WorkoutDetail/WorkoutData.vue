<template>
  <div id="workout-info">
    <div class="workout-data">
      <i class="fa fa-clock-o" aria-hidden="true" />
      {{ t('workouts.DURATION') }}: <span>{{ workout.moving }}</span>
      <WorkoutRecord :workout="workout" record_type="LD" />
      <div v-if="withPause">
        ({{ t('workouts.PAUSES') }}: <span>{{ workout.pauses }}</span> -
        {{ t('workouts.TOTAL_DURATION') }}: <span>{{ workout.duration }})</span>
      </div>
    </div>
    <div class="workout-data">
      <i class="fa fa-road" aria-hidden="true" />
      {{ t('workouts.DISTANCE') }}: <span>{{ workout.distance }} km</span>
      <WorkoutRecord :workout="workout" record_type="FD" />
    </div>
    <div class="workout-data">
      <i class="fa fa-tachometer" aria-hidden="true" />
      {{ t('workouts.AVERAGE_SPEED') }}:
      <span>{{ workout.ave_speed }} km/h</span
      ><WorkoutRecord :workout="workout" record_type="AS" /><br />
      {{ t('workouts.MAX_SPEED') }}: <span>{{ workout.max_speed }} km/h</span>
      <WorkoutRecord :workout="workout" record_type="MS" />
    </div>
    <div class="workout-data">
      <img class="mountains" src="/img/misc/mountains.svg" />
      {{ t('workouts.MIN_ALTITUDE') }}: <span>{{ workout.min_alt }} m</span
      ><br />
      {{ t('workouts.MAX_ALTITUDE') }}: <span>{{ workout.max_alt }} m</span>
    </div>
    <div class="workout-data">
      <i class="fa fa-location-arrow" aria-hidden="true" />
      {{ t('workouts.ASCENT') }}: <span>{{ workout.ascent }} m</span><br />
      {{ t('workouts.DESCENT') }}: <span>{{ workout.descent }} m</span>
    </div>
    <WorkoutWeather :workout="workout" />
  </div>
</template>

<script lang="ts">
  import { PropType, defineComponent, computed } from 'vue'
  import { useI18n } from 'vue-i18n'

  import WorkoutRecord from '@/components/Workout/WorkoutDetail/WorkoutRecord.vue'
  import WorkoutWeather from '@/components/Workout/WorkoutDetail/WorkoutWeather.vue'
  import { IWorkout } from '@/types/workouts'
  export default defineComponent({
    name: 'WorkoutData',
    components: {
      WorkoutRecord,
      WorkoutWeather,
    },
    props: {
      workout: {
        type: Object as PropType<IWorkout>,
        required: true,
      },
    },
    setup(props) {
      const { t } = useI18n()
      return {
        withPause: computed(
          () =>
            props.workout.pauses !== '0:00:00' && props.workout.pauses !== null
        ),
        t,
      }
    },
  })
</script>

<style lang="scss" scoped>
  @import '~@/scss/base';
  #workout-info {
    display: flex;
    flex-direction: column;
    padding: $default-padding $default-padding * 2;
    width: 100%;
    .mountains {
      margin-bottom: -3px;
      height: 16px;
      filter: var(--workout-img-color);
    }
    .workout-data {
      text-transform: capitalize;
      padding: $default-padding * 0.5 0;

      span {
        font-weight: bold;
        text-transform: lowercase;
      }
    }

    @media screen and (max-width: $small-limit) {
      padding: $default-padding;
    }
  }
</style>
