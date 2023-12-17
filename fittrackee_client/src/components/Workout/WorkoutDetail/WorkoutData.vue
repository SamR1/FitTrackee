<template>
  <div id="workout-info">
    <div class="workout-data">
      <i class="fa fa-clock-o" aria-hidden="true" />
      <span class="label"> {{ $t('workouts.DURATION') }} </span>:
      <span class="value">{{ workoutObject.moving }}</span>
      <WorkoutRecord :workoutObject="workoutObject" recordType="LD" />
      <div v-if="withPause">
        ({{ $t('workouts.PAUSES') }}:
        <span class="value">{{ workoutObject.pauses }}</span> -
        {{ $t('workouts.TOTAL_DURATION') }}:
        <span class="value">{{ workoutObject.duration }})</span>
      </div>
    </div>
    <div class="workout-data" v-if="workoutObject.distance !== null">
      <i class="fa fa-road" aria-hidden="true" />
      <span class="label"> {{ $t('workouts.DISTANCE') }} </span>:
      <Distance
        :distance="workoutObject.distance"
        :digits="3"
        unitFrom="km"
        :strong="true"
        :useImperialUnits="useImperialUnits"
      />
      <WorkoutRecord :workoutObject="workoutObject" recordType="FD" />
    </div>
    <div
      class="workout-data"
      v-if="workoutObject.aveSpeed !== null && workoutObject.maxSpeed !== null"
    >
      <i class="fa fa-tachometer" aria-hidden="true" />
      <span class="label">{{ $t('workouts.AVERAGE_SPEED') }}</span
      >:
      <Distance
        :distance="workoutObject.aveSpeed"
        unitFrom="km"
        :speed="true"
        :strong="true"
        :useImperialUnits="useImperialUnits"
      />
      <WorkoutRecord :workoutObject="workoutObject" recordType="AS" /><br />
      <span class="label"> {{ $t('workouts.MAX_SPEED') }} </span>:
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
      <span class="label">{{ $t('workouts.MIN_ALTITUDE') }}</span
      >:
      <Distance
        :distance="workoutObject.minAlt"
        unitFrom="m"
        :strong="true"
        :useImperialUnits="useImperialUnits"
      /><br />
      <span class="label">{{ $t('workouts.MAX_ALTITUDE') }}</span
      >:
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
      <span class="label">{{ $t('workouts.ASCENT') }}</span
      >:
      <Distance
        :distance="workoutObject.ascent"
        unitFrom="m"
        :strong="true"
        :useImperialUnits="useImperialUnits"
      />
      <WorkoutRecord
        v-if="displayHARecord"
        :workoutObject="workoutObject"
        recordType="HA"
      />
      <br />
      <span class="label"> {{ $t('workouts.DESCENT') }} </span>:
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
  import type { IWorkoutObject } from '@/types/workouts'

  interface Props {
    workoutObject: IWorkoutObject
    useImperialUnits: boolean
    displayHARecord: boolean
  }
  const props = defineProps<Props>()

  const { displayHARecord, workoutObject, useImperialUnits } = toRefs(props)
  const withPause = computed(
    () =>
      props.workoutObject.pauses !== '0:00:00' &&
      props.workoutObject.pauses !== null
  )
</script>

<style lang="scss" scoped>
  @import '~@/scss/vars.scss';
  #workout-info {
    display: flex;
    flex-direction: column;
    padding: $default-padding $default-padding * 2;
    width: 100%;

    .fa,
    .mountains {
      padding-right: $default-padding * 0.5;
    }
    .mountains {
      filter: var(--mountains-filter);
    }

    .workout-data {
      padding: $default-padding * 0.5 0;
      .label {
        text-transform: capitalize;
      }
      .value {
        font-weight: bold;
        text-transform: lowercase;
      }
    }

    @media screen and (max-width: $small-limit) {
      padding: $default-padding;
    }
  }
</style>
