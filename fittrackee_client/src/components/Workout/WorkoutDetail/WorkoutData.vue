<template>
  <div id="workout-info">
    <div class="workout-data" v-if="workoutObject.source !== null">
      <i class="fa fa-info-circle" aria-hidden="true" />
      <span class="label"> {{ $t('workouts.SOURCE') }} </span>:
      <span class="label">{{ workoutObject.source }}</span>
    </div>
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
    <div
      class="workout-data"
      v-if="
        workoutObject.aveCadence !== null && workoutObject.maxCadence !== null
      "
    >
      <img
        class="cadence"
        src="/img/workouts/cadence.svg"
        :alt="$t('workouts.CADENCE')"
      />
      <span class="label">{{ $t('workouts.AVERAGE_CADENCE') }}</span
      >:
      <span class="value" :title="t(`workouts.UNITS.${cadenceUnit}.LABEL`)"
        >{{ workoutObject.aveCadence }} {{ cadenceUnit }}</span
      >
      <br />
      <span class="label"> {{ $t('workouts.MAX_CADENCE') }}</span
      >:
      <span class="value" :title="t(`workouts.UNITS.${cadenceUnit}.LABEL`)"
        >{{ workoutObject.maxCadence }} {{ cadenceUnit }}</span
      >
    </div>
    <div
      class="workout-data"
      v-if="workoutObject.aveHr !== null && workoutObject.maxHr !== null"
    >
      <i class="fa fa-heartbeat" aria-hidden="true" />
      <span class="label">{{ $t('workouts.AVERAGE_HR') }}</span
      >:
      <span class="value" :title="t(`workouts.UNITS.bpm.LABEL`)"
        >{{ workoutObject.aveHr }} {{ t(`workouts.UNITS.bpm.UNIT`) }}</span
      >
      <br />
      <span class="label"> {{ $t('workouts.MAX_HR') }}</span
      >:
      <span class="value" :title="t(`workouts.UNITS.bpm.LABEL`)"
        >{{ workoutObject.maxHr }} {{ t(`workouts.UNITS.bpm.UNIT`) }}</span
      >
    </div>
    <WorkoutWeather
      :workoutObject="workoutObject"
      :useImperialUnits="useImperialUnits"
    />
  </div>
</template>

<script setup lang="ts">
  import { computed, toRefs } from 'vue'
  import type { ComputedRef } from 'vue'
  import { useI18n } from 'vue-i18n'

  import WorkoutRecord from '@/components/Workout/WorkoutDetail/WorkoutRecord.vue'
  import WorkoutWeather from '@/components/Workout/WorkoutDetail/WorkoutWeather.vue'
  import type { IWorkoutObject } from '@/types/workouts'

  interface Props {
    workoutObject: IWorkoutObject
    useImperialUnits: boolean
    displayHARecord: boolean
    cadenceUnit: string
  }
  const props = defineProps<Props>()
  const { displayHARecord, workoutObject, useImperialUnits } = toRefs(props)

  const { t } = useI18n()

  const withPause: ComputedRef<boolean> = computed(
    () =>
      workoutObject.value.pauses !== '0:00:00' &&
      workoutObject.value.pauses !== null
  )
</script>

<style lang="scss" scoped>
  @use '~@/scss/vars.scss' as *;
  #workout-info {
    display: flex;
    flex-direction: column;
    padding: $default-padding $default-padding * 2;
    width: 100%;

    .fa,
    .mountains,
    .cadence {
      padding-right: $default-padding * 0.5;
    }

    .workout-data {
      padding: $default-padding * 0.25 0;
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
