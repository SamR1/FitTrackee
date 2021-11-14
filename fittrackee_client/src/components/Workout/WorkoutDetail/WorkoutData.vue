<template>
  <div id="workout-info">
    <div class="workout-data">
      <i class="fa fa-clock-o" aria-hidden="true" />
      {{ $t('workouts.DURATION') }}: <span>{{ workoutObject.moving }}</span>
      <WorkoutRecord :workoutObject="workoutObject" recordType="LD" />
      <div v-if="withPause">
        ({{ $t('workouts.PAUSES') }}: <span>{{ workoutObject.pauses }}</span> -
        {{ $t('workouts.TOTAL_DURATION') }}:
        <span>{{ workoutObject.duration }})</span>
      </div>
    </div>
    <div class="workout-data">
      <i class="fa fa-road" aria-hidden="true" />
      {{ $t('workouts.DISTANCE') }}:
      <Distance
        :distance="workoutObject.distance"
        :digits="3"
        unitFrom="km"
        :strong="true"
        :useImperialUnits="useImperialUnits"
      />
      <WorkoutRecord :workoutObject="workoutObject" recordType="FD" />
    </div>
    <div class="workout-data">
      <i class="fa fa-tachometer" aria-hidden="true" />
      {{ $t('workouts.AVERAGE_SPEED') }}:
      <Distance
        :distance="workoutObject.aveSpeed"
        unitFrom="km"
        :speed="true"
        :strong="true"
        :useImperialUnits="useImperialUnits"
      />
      <WorkoutRecord :workoutObject="workoutObject" recordType="AS" /><br />
      {{ $t('workouts.MAX_SPEED') }}:
      <Distance
        :distance="workoutObject.maxSpeed"
        unitFrom="km"
        :speed="true"
        :strong="true"
        :useImperialUnits="useImperialUnits"
      />
      <WorkoutRecord :workoutObject="workoutObject" recordType="MS" />
    </div>
    <div
      class="workout-data"
      v-if="workoutObject.maxAlt !== null && workoutObject.minAlt !== null"
    >
      <img
        class="mountains"
        src="/img/workouts/mountains.svg"
        :alt="$t('workouts.ELEVATION')"
      />
      {{ $t('workouts.MIN_ALTITUDE') }}:
      <Distance
        :distance="workoutObject.minAlt"
        unitFrom="m"
        :strong="true"
        :useImperialUnits="useImperialUnits"
      /><br />
      {{ $t('workouts.MAX_ALTITUDE') }}:
      <Distance
        :distance="workoutObject.maxAlt"
        unitFrom="m"
        :strong="true"
        :useImperialUnits="useImperialUnits"
      />
    </div>
    <div
      class="workout-data"
      v-if="workoutObject.ascent !== null && workoutObject.descent !== null"
    >
      <i class="fa fa-location-arrow" aria-hidden="true" />
      {{ $t('workouts.ASCENT') }}:
      <Distance
        :distance="workoutObject.ascent"
        unitFrom="m"
        :strong="true"
        :useImperialUnits="useImperialUnits"
      /><br />
      {{ $t('workouts.DESCENT') }}:
      <Distance
        :distance="workoutObject.descent"
        unitFrom="m"
        :strong="true"
        :useImperialUnits="useImperialUnits"
      />
    </div>
    <WorkoutWeather
      :workoutObject="workoutObject"
      :useImperialUnits="useImperialUnits"
    />
  </div>
</template>

<script setup lang="ts">
  import { computed, toRefs } from 'vue'

  import WorkoutRecord from '@/components/Workout/WorkoutDetail/WorkoutRecord.vue'
  import WorkoutWeather from '@/components/Workout/WorkoutDetail/WorkoutWeather.vue'
  import { IWorkoutObject } from '@/types/workouts'

  interface Props {
    workoutObject: IWorkoutObject
    useImperialUnits: boolean
  }
  const props = defineProps<Props>()

  const { workoutObject, useImperialUnits } = toRefs(props)
  const withPause = computed(
    () =>
      props.workoutObject.pauses !== '0:00:00' &&
      props.workoutObject.pauses !== null
  )
</script>

<style lang="scss" scoped>
  @import '~@/scss/base';
  #workout-info {
    display: flex;
    flex-direction: column;
    padding: $default-padding $default-padding * 2;
    width: 100%;

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
