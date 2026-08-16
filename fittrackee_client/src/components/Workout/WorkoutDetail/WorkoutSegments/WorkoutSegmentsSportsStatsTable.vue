<template>
  <table :class="[tableClass]">
    <thead>
      <tr>
        <th></th>
        <th v-for="sportStats in statsWithSport" :key="sportStats.sport_id">
          <div class="sport">
            <SportImage
              :sport-label="sportStats.sport?.label"
              :color="sportStats.sport?.color"
            />
            {{ $t(`sports.${sportStats.sport?.label}.LABEL`) }}
          </div>
        </th>
      </tr>
    </thead>
    <tbody>
      <tr class="sport-label">
        <td class="value-label capitalize"></td>
        <td class="value">
          <div class="sport-label-img">
            <SportImage
              :sport-label="statsWithSport[0].sport?.label"
              :color="statsWithSport[0].sport?.color"
            />
            {{ $t(`sports.${statsWithSport[0].sport?.label}.LABEL`) }}
          </div>
        </td>
      </tr>
      <tr>
        <td class="value-label capitalize capitalize">
          {{ $t('workouts.DURATION') }}
        </td>
        <td
          class="value"
          v-for="sportStats in statsWithSport"
          :key="sportStats.sport_id"
        >
          <span class="cell-heading">{{ $t('workouts.DURATION') }}</span>
          {{ sportStats.moving }}
        </td>
      </tr>
      <tr
        v-if="
          Object.values(statsWithSport).some(
            (stats) => stats.pauses !== '0:00:00'
          )
        "
      >
        <td class="value-label capitalize">
          {{ $t('workouts.PAUSES') }}
        </td>
        <td
          class="value"
          v-for="sportStats in statsWithSport"
          :key="sportStats.sport_id"
        >
          <span class="cell-heading">{{ $t('workouts.PAUSES') }}</span>
          {{ sportStats.pauses }}
        </td>
      </tr>
      <tr>
        <td class="value-label capitalize">
          {{ $t('workouts.DISTANCE') }}
        </td>
        <td
          class="value"
          v-for="sportStats in statsWithSport"
          :key="sportStats.sport_id"
        >
          <span class="cell-heading">{{ $t('workouts.DISTANCE') }}</span>
          <Distance
            v-if="sportStats.distance"
            :distance="sportStats.distance"
            :digits="3"
            unitFrom="km"
            :useImperialUnits="displayOptions.useImperialUnits"
          />
        </td>
      </tr>
      <tr
        v-if="
          Object.values(statsWithSport).some((stats) => stats.ave_pace !== null)
        "
      >
        <td class="value-label capitalize">
          {{ $t('workouts.AVERAGE_PACE') }}
        </td>
        <td
          class="value"
          v-for="sportStats in statsWithSport"
          :key="sportStats.sport_id"
        >
          <span class="cell-heading">{{ $t('workouts.AVERAGE_PACE') }}</span>
          <Pace
            v-if="sportStats.ave_pace !== null"
            :pace="sportStats.ave_pace"
            :useImperialUnits="displayOptions.useImperialUnits"
          />
        </td>
      </tr>
      <tr
        v-if="
          Object.values(statsWithSport).some(
            (stats) => stats.best_pace !== null
          )
        "
      >
        <td class="value-label capitalize">
          {{ $t('workouts.BEST_PACE') }}
        </td>
        <td
          class="value"
          v-for="sportStats in statsWithSport"
          :key="sportStats.sport_id"
        >
          <span class="cell-heading">{{ $t('workouts.BEST_PACE') }}</span>
          <Pace
            v-if="sportStats.best_pace !== null"
            :pace="sportStats.best_pace"
            :useImperialUnits="displayOptions.useImperialUnits"
          />
        </td>
      </tr>
      <tr
        v-if="
          Object.values(statsWithSport).some(
            (stats) => stats.ave_speed !== null
          )
        "
      >
        <td class="value-label capitalize">
          {{ $t('workouts.AVERAGE_SPEED') }}
        </td>
        <td
          class="value"
          v-for="sportStats in statsWithSport"
          :key="sportStats.sport_id"
        >
          <span class="cell-heading">{{ $t('workouts.AVERAGE_SPEED') }}</span>
          <Distance
            v-if="sportStats.ave_speed"
            :distance="sportStats.ave_speed"
            unitFrom="km"
            speed
            :useImperialUnits="displayOptions.useImperialUnits"
          />
        </td>
      </tr>
      <tr
        v-if="
          Object.values(statsWithSport).some(
            (stats) => stats.max_speed !== null
          )
        "
      >
        <td class="value-label capitalize">
          {{ $t('workouts.MAX_SPEED') }}
        </td>
        <td
          class="value"
          v-for="sportStats in statsWithSport"
          :key="sportStats.sport_id"
        >
          <span class="cell-heading">{{ $t('workouts.MAX_SPEED') }}</span>
          <Distance
            v-if="sportStats.max_speed"
            :distance="sportStats.max_speed"
            unitFrom="km"
            speed
            :useImperialUnits="displayOptions.useImperialUnits"
          />
        </td>
      </tr>
      <tr
        v-if="
          Object.values(statsWithSport).some((stats) => stats.min_alt !== null)
        "
      >
        <td class="value-label capitalize">
          {{ $t('workouts.MIN_ALTITUDE') }}
        </td>
        <td
          class="value"
          v-for="sportStats in statsWithSport"
          :key="sportStats.sport_id"
        >
          <span class="cell-heading">{{ $t('workouts.MIN_ALTITUDE') }}</span>
          <Distance
            v-if="sportStats.min_alt"
            :distance="sportStats.min_alt"
            unitFrom="m"
            :useImperialUnits="displayOptions.useImperialUnits"
          />
        </td>
      </tr>
      <tr
        v-if="
          Object.values(statsWithSport).some((stats) => stats.max_alt !== null)
        "
      >
        <td class="value-label capitalize">
          {{ $t('workouts.MAX_ALTITUDE') }}
        </td>
        <td
          class="value"
          v-for="sportStats in statsWithSport"
          :key="sportStats.sport_id"
        >
          <span class="cell-heading">{{ $t('workouts.MAX_ALTITUDE') }}</span>
          <Distance
            v-if="sportStats.max_alt"
            :distance="sportStats.max_alt"
            unitFrom="m"
            :useImperialUnits="displayOptions.useImperialUnits"
          />
        </td>
      </tr>
      <tr
        v-if="
          Object.values(statsWithSport).some(
            (stats) => stats.ascent === undefined
          )
        "
      >
        <td class="value-label capitalize">
          {{ $t('workouts.ASCENT') }}
        </td>
        <td
          class="value"
          v-for="sportStats in statsWithSport"
          :key="sportStats.sport_id"
        >
          <span class="cell-heading">{{ $t('workouts.ASCENT') }}</span>
          <Distance
            v-if="sportStats.ascent"
            :distance="sportStats.ascent"
            unitFrom="m"
            :useImperialUnits="displayOptions.useImperialUnits"
          />
        </td>
      </tr>
      <tr
        v-if="
          Object.values(statsWithSport).some(
            (stats) => stats.descent === undefined
          )
        "
      >
        <td class="value-label capitalize">
          {{ $t('workouts.DESCENT') }}
        </td>
        <td
          class="value"
          v-for="sportStats in statsWithSport"
          :key="sportStats.sport_id"
        >
          <span class="cell-heading">{{ $t('workouts.DESCENT') }}</span>
          <Distance
            v-if="sportStats.descent"
            :distance="sportStats.descent"
            unitFrom="m"
            :useImperialUnits="displayOptions.useImperialUnits"
          />
        </td>
      </tr>
      <tr
        v-if="
          Object.values(statsWithSport).some(
            (stats) => stats.ave_cadence !== null
          )
        "
      >
        <td class="value-label capitalize">
          {{ $t('workouts.AVERAGE_CADENCE') }}
        </td>
        <td
          class="value"
          v-for="sportStats in statsWithSport"
          :key="sportStats.sport_id"
        >
          <span class="cell-heading">{{ $t('workouts.AVERAGE_CADENCE') }}</span>
          <span
            v-if="sportStats.ave_cadence"
            class="value"
            :title="$t(`workouts.UNITS.${cadenceUnit}.LABEL`)"
          >
            {{ sportStats.ave_cadence }}
            {{ $t(`workouts.UNITS.${cadenceUnit}.UNIT`) }}
          </span>
        </td>
      </tr>
      <tr
        v-if="
          Object.values(statsWithSport).some(
            (stats) => stats.max_cadence !== null
          )
        "
      >
        <td class="value-label capitalize">
          {{ $t('workouts.MAX_CADENCE') }}
        </td>
        <td
          class="value"
          v-for="sportStats in statsWithSport"
          :key="sportStats.sport_id"
        >
          <span class="cell-heading">{{ $t('workouts.MAX_CADENCE') }}</span>
          <span
            v-if="sportStats.max_cadence"
            class="value"
            :title="$t(`workouts.UNITS.${cadenceUnit}.LABEL`)"
          >
            {{ sportStats.max_cadence }}
            {{ $t(`workouts.UNITS.${cadenceUnit}.UNIT`) }}
          </span>
        </td>
      </tr>
      <tr
        v-if="
          Object.values(statsWithSport).some(
            (stats) => stats.ave_power !== null
          )
        "
      >
        <td class="value-label capitalize">
          {{ $t('workouts.AVERAGE_POWER') }}
        </td>
        <td
          class="value"
          v-for="sportStats in statsWithSport"
          :key="sportStats.sport_id"
        >
          <span class="cell-heading">{{ $t('workouts.AVERAGE_POWER') }}</span>
          <span
            v-if="sportStats.ave_power"
            class="value"
            :title="$t('workouts.UNITS.watt.LABEL')"
          >
            {{ sportStats.ave_power }} {{ $t('workouts.UNITS.watt.UNIT') }}
          </span>
        </td>
      </tr>
      <tr
        v-if="
          Object.values(statsWithSport).some(
            (stats) => stats.max_power !== null
          )
        "
      >
        <td class="value-label capitalize">
          {{ $t('workouts.MAX_POWER') }}
        </td>
        <td
          class="value"
          v-for="sportStats in statsWithSport"
          :key="sportStats.sport_id"
        >
          <span class="cell-heading">{{ $t('workouts.MAX_POWER') }}</span>
          <span
            v-if="sportStats.max_power"
            class="value"
            :title="$t('workouts.UNITS.watt.LABEL')"
          >
            {{ sportStats.max_power }} {{ $t('workouts.UNITS.watt.UNIT') }}
          </span>
        </td>
      </tr>
      <tr
        v-if="
          Object.values(statsWithSport).some((stats) => stats.ave_hr !== null)
        "
      >
        <td class="value-label capitalize">
          {{ $t('workouts.AVERAGE_HR') }}
        </td>
        <td
          class="value"
          v-for="sportStats in statsWithSport"
          :key="sportStats.sport_id"
        >
          <span class="cell-heading">{{ $t('workouts.AVERAGE_HR') }}</span>
          <span
            v-if="sportStats.ave_hr"
            class="value"
            :title="$t(`workouts.UNITS.bpm.LABEL`)"
          >
            {{ sportStats.ave_hr }} {{ $t(`workouts.UNITS.bpm.UNIT`) }}
          </span>
        </td>
      </tr>
      <tr
        v-if="
          Object.values(statsWithSport).some((stats) => stats.max_hr !== null)
        "
      >
        <td class="value-label capitalize">
          {{ $t('workouts.MAX_HR') }}
        </td>
        <td
          class="value"
          v-for="sportStats in statsWithSport"
          :key="sportStats.sport_id"
        >
          <span class="cell-heading">{{ $t('workouts.MAX_HR') }}</span>
          <span
            v-if="sportStats.max_hr"
            class="value"
            :title="$t(`workouts.UNITS.bpm.LABEL`)"
          >
            {{ sportStats.max_hr }} {{ $t(`workouts.UNITS.bpm.UNIT`) }}
          </span>
        </td>
      </tr>
      <tr v-if="Object.values(statsWithSport).some((stats) => stats.calories)">
        <td class="value-label capitalize">
          {{ $t('workouts.CALORIES') }}
        </td>
        <td
          class="value"
          v-for="sportStats in statsWithSport"
          :key="sportStats.sport_id"
        >
          <span class="cell-heading">{{ $t('workouts.CALORIES') }}</span>
          <span
            v-if="sportStats.calories"
            class="value"
            :title="$t(`workouts.UNITS.kcal.LABEL`)"
          >
            {{ sportStats.calories }}
            {{ $t(`workouts.UNITS.kcal.UNIT`) }}
          </span>
        </td>
      </tr>
    </tbody>
  </table>
</template>

<script setup lang="ts">
  import { computed, toRefs } from 'vue'

  import type { IDisplayOptions } from '@/types/application.ts'
  import type { IMultiSportsStats, TCadenceUnit } from '@/types/workouts.ts'

  interface Props {
    statsWithSport: IMultiSportsStats[]
    cadenceUnit: TCadenceUnit
    displayOptions: IDisplayOptions
  }
  const props = defineProps<Props>()
  const { statsWithSport } = toRefs(props)
  const tableClass = computed(() => `cols-${statsWithSport.value.length}`)
</script>

<style scoped lang="scss">
  @use '~@/scss/vars.scss' as *;

  table {
    min-width: 400px;
    border-collapse: collapse;
    margin: $default-margin 0;

    &.cols-2 {
      .value {
        width: 33%;
      }
    }
    &.cols-3 {
      .value {
        width: 25%;
      }
    }

    th,
    td {
      padding: $default-padding;
    }

    th {
      border-bottom: 2px solid var(--card-border-color);
    }

    td {
      border-bottom: 1px solid var(--card-border-color);
    }
    tr:last-child td {
      border-bottom: none;
    }

    .value-label {
      font-weight: bold;
    }
    .value {
      text-align: right;
    }

    .cell-heading {
      display: none;
    }

    .sport {
      display: flex;
      gap: $default-padding * 0.5;
      min-width: 50px;
      align-items: center;
      justify-content: center;

      .sport-img {
        min-width: 20px;
        height: 20px;
        width: 20px;
        margin: 0;
      }
    }
    .sport-label {
      display: none;
    }
  }
  @media screen and (max-width: $x-small-limit) {
    table {
      min-width: initial;
      width: 100%;
      &.cols-2,
      &.cols-3 {
        .value {
          width: initial;
        }
      }

      tr {
        margin-bottom: 0;
      }

      .value-label {
        display: none;
      }
      .value {
        text-align: center;
      }
      .cell-heading {
        display: initial;
      }

      .sport-label {
        display: flex;

        .sport-label-img {
          display: flex;
          justify-content: center;
          align-items: center;
          gap: $default-padding;
          font-weight: bold;

          .sport-img {
            height: 20px;
            width: 20px;
            margin: 0;
          }
        }

        .value {
          width: 100%;
        }
      }
    }
  }
</style>
