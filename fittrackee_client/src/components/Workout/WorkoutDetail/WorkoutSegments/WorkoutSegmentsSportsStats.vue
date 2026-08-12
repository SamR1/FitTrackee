<template>
  <div id="workout-sports-stats">
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
        <tr>
          <td class="value-label">
            {{ $t('workouts.DURATION') }}
          </td>
          <td
            class="value"
            v-for="sportStats in statsWithSport"
            :key="sportStats.sport_id"
          >
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
          <td class="value-label">
            {{ $t('workouts.PAUSES') }}
          </td>
          <td
            class="value"
            v-for="sportStats in statsWithSport"
            :key="sportStats.sport_id"
          >
            {{ sportStats.pauses }}
          </td>
        </tr>
        <tr>
          <td class="value-label">
            {{ $t('workouts.DISTANCE') }}
          </td>
          <td
            class="value"
            v-for="sportStats in statsWithSport"
            :key="sportStats.sport_id"
          >
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
            Object.values(statsWithSport).some(
              (stats) => stats.ave_pace !== null
            )
          "
        >
          <td class="value-label">
            {{ $t('workouts.AVERAGE_PACE') }}
          </td>
          <td
            class="value"
            v-for="sportStats in statsWithSport"
            :key="sportStats.sport_id"
          >
            <Pace
              v-if="sportStats.ave_pace !== null"
              :pace="sportStats.ave_pace"
              :useImperialUnits="displayOptions.useImperialUnits"
            />
          </td>
        </tr>
        <tr>
          <td class="value-label">
            {{ $t('workouts.BEST_PACE') }}
          </td>
          <td
            class="value"
            v-for="sportStats in statsWithSport"
            :key="sportStats.sport_id"
          >
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
          <td class="value-label">
            {{ $t('workouts.AVERAGE_SPEED') }}
          </td>
          <td
            class="value"
            v-for="sportStats in statsWithSport"
            :key="sportStats.sport_id"
          >
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
          <td class="value-label">
            {{ $t('workouts.MAX_SPEED') }}
          </td>
          <td
            class="value"
            v-for="sportStats in statsWithSport"
            :key="sportStats.sport_id"
          >
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
            Object.values(statsWithSport).some(
              (stats) => stats.min_alt !== null
            )
          "
        >
          <td class="value-label">
            {{ $t('workouts.MIN_ALTITUDE') }}
          </td>
          <td
            class="value"
            v-for="sportStats in statsWithSport"
            :key="sportStats.sport_id"
          >
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
            Object.values(statsWithSport).some(
              (stats) => stats.max_alt !== null
            )
          "
        >
          <td class="value-label">
            {{ $t('workouts.MAX_ALTITUDE') }}
          </td>
          <td
            class="value"
            v-for="sportStats in statsWithSport"
            :key="sportStats.sport_id"
          >
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
            Object.values(statsWithSport).some((stats) => stats.ascent !== null)
          "
        >
          <td class="value-label">
            {{ $t('workouts.ASCENT') }}
          </td>
          <td
            class="value"
            v-for="sportStats in statsWithSport"
            :key="sportStats.sport_id"
          >
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
              (stats) => stats.descent !== null
            )
          "
        >
          <td class="value-label">
            {{ $t('workouts.DESCENT') }}
          </td>
          <td
            class="value"
            v-for="sportStats in statsWithSport"
            :key="sportStats.sport_id"
          >
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
          <td class="value-label">
            {{ $t('workouts.AVERAGE_CADENCE') }}
          </td>
          <td
            class="value"
            v-for="sportStats in statsWithSport"
            :key="sportStats.sport_id"
          >
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
          <td class="value-label">
            {{ $t('workouts.MAX_CADENCE') }}
          </td>
          <td
            class="value"
            v-for="sportStats in statsWithSport"
            :key="sportStats.sport_id"
          >
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
          <td class="value-label">
            {{ $t('workouts.AVERAGE_POWER') }}
          </td>
          <td
            class="value"
            v-for="sportStats in statsWithSport"
            :key="sportStats.sport_id"
          >
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
          <td class="value-label">
            {{ $t('workouts.MAX_POWER') }}
          </td>
          <td
            class="value"
            v-for="sportStats in statsWithSport"
            :key="sportStats.sport_id"
          >
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
          <td class="value-label">
            {{ $t('workouts.AVERAGE_HR') }}
          </td>
          <td
            class="value"
            v-for="sportStats in statsWithSport"
            :key="sportStats.sport_id"
          >
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
          <td class="value-label">
            {{ $t('workouts.MAX_HR') }}
          </td>
          <td
            class="value"
            v-for="sportStats in statsWithSport"
            :key="sportStats.sport_id"
          >
            <span
              v-if="sportStats.max_hr"
              class="value"
              :title="$t(`workouts.UNITS.bpm.LABEL`)"
            >
              {{ sportStats.max_hr }} {{ $t(`workouts.UNITS.bpm.UNIT`) }}
            </span>
          </td>
        </tr>
        <tr
          v-if="Object.values(statsWithSport).some((stats) => stats.calories)"
        >
          <td class="value-label">
            {{ $t('workouts.CALORIES') }}
          </td>
          <td
            class="value"
            v-for="sportStats in statsWithSport"
            :key="sportStats.sport_id"
          >
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
  </div>
</template>

<script setup lang="ts">
  import { computed, type ComputedRef, toRefs } from 'vue'

  import useSports from '@/composables/useSports.ts'
  import { ROOT_STORE } from '@/store/constants.ts'
  import type { IDisplayOptions } from '@/types/application.ts'
  import type { IAuthUserProfile } from '@/types/user.ts'
  import type { IMultiSportsStats, TCadenceUnit } from '@/types/workouts.ts'
  import { useStore } from '@/use/useStore.ts'

  interface Props {
    authUser: IAuthUserProfile
    sportsStats: Record<number, IMultiSportsStats>
    cadenceUnit: TCadenceUnit
  }
  const props = defineProps<Props>()
  const { sportsStats } = toRefs(props)

  const store = useStore()

  const { getObjectSport } = useSports()

  const displayOptions: ComputedRef<IDisplayOptions> = computed(
    () => store.getters[ROOT_STORE.GETTERS.DISPLAY_OPTIONS]
  )
  const statsWithSport = computed(() =>
    Object.entries(sportsStats.value).map(([key, value]) => {
      return {
        ...value,
        sport: getObjectSport({ sport_id: +key }),
      }
    })
  )
  const tableClass = computed(
    () => `cols-${Object.keys(sportsStats.value).length}`
  )
</script>

<style scoped lang="scss">
  @use '~@/scss/vars.scss' as *;
  #workout-sports-stats {
    overflow-x: scroll;

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

      .sport {
        display: flex;
        gap: $default-padding * 0.5;
        min-width: 50px;
        align-items: center;
        justify-content: center;
        text-wrap: nowrap;

        .sport-img {
          height: 20px;
          width: 20px;
          margin: 0;
        }
      }
    }
  }
</style>
