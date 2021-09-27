<template>
  <div id="workout-info">
    <div class="workout-data">
      <i class="fa fa-clock-o" aria-hidden="true" />
      {{ t('workouts.DURATION') }}: <span>{{ workoutObject.moving }}</span>
      <WorkoutRecord :workoutObject="workoutObject" record_type="LD" />
      <div v-if="withPause">
        ({{ t('workouts.PAUSES') }}: <span>{{ workoutObject.pauses }}</span> -
        {{ t('workouts.TOTAL_DURATION') }}:
        <span>{{ workoutObject.duration }})</span>
      </div>
    </div>
    <div class="workout-data">
      <i class="fa fa-road" aria-hidden="true" />
      {{ t('workouts.DISTANCE') }}: <span>{{ workoutObject.distance }} km</span>
      <WorkoutRecord :workoutObject="workoutObject" record_type="FD" />
    </div>
    <div class="workout-data">
      <i class="fa fa-tachometer" aria-hidden="true" />
      {{ t('workouts.AVERAGE_SPEED') }}:
      <span>{{ workoutObject.aveSpeed }} km/h</span
      ><WorkoutRecord :workoutObject="workoutObject" record_type="AS" /><br />
      {{ t('workouts.MAX_SPEED') }}:
      <span>{{ workoutObject.maxSpeed }} km/h</span>
      <WorkoutRecord :workoutObject="workoutObject" record_type="MS" />
    </div>
    <div
      class="workout-data"
      v-if="workoutObject.maxAlt !== null && workoutObject.minAlt !== null"
    >
      <img class="mountains" src="/img/misc/mountains.svg" />
      {{ t('workouts.MIN_ALTITUDE') }}: <span>{{ workoutObject.minAlt }} m</span
      ><br />
      {{ t('workouts.MAX_ALTITUDE') }}:
      <span>{{ workoutObject.maxAlt }} m</span>
    </div>
    <div
      class="workout-data"
      v-if="workoutObject.ascent !== null && workoutObject.descent !== null"
    >
      <i class="fa fa-location-arrow" aria-hidden="true" />
      {{ t('workouts.ASCENT') }}: <span>{{ workoutObject.ascent }} m</span
      ><br />
      {{ t('workouts.DESCENT') }}: <span>{{ workoutObject.descent }} m</span>
    </div>
    <WorkoutWeather :workoutObject="workoutObject" />
  </div>
</template>

<script lang="ts">
  import { PropType, defineComponent, computed } from 'vue'
  import { useI18n } from 'vue-i18n'

  import WorkoutRecord from '@/components/Workout/WorkoutDetail/WorkoutRecord.vue'
  import WorkoutWeather from '@/components/Workout/WorkoutDetail/WorkoutWeather.vue'
  import { IWorkoutObject } from '@/types/workouts'
  export default defineComponent({
    name: 'WorkoutData',
    components: {
      WorkoutRecord,
      WorkoutWeather,
    },
    props: {
      workoutObject: {
        type: Object as PropType<IWorkoutObject>,
        required: true,
      },
    },
    setup(props) {
      const { t } = useI18n()
      return {
        withPause: computed(
          () =>
            props.workoutObject.pauses !== '0:00:00' &&
            props.workoutObject.pauses !== null
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
