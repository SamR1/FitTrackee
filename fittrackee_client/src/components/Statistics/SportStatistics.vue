<template>
  <div id="sport-statistics">
    <label for="sport"> {{ $t('workouts.SPORT', 1) }}: </label>
    <select id="sport" v-model="sportId" @change="updateParams">
      <option
        v-for="selectedSport in translatedSports"
        :value="selectedSport.id"
        :key="selectedSport.id"
      >
        {{ selectedSport.translatedLabel }}
      </option>
    </select>
    <div v-if="selectedSport" class="sport-statistics">
      <div class="sport-img-label">
        <SportImage
          :sport-label="selectedSport.label"
          :color="selectedSport.color"
        />
        <div class="sport-label">{{ selectedSport.translatedLabel }}</div>
      </div>
      <div>
        <div class="label">
          <i class="fa fa-line-chart custom-fa-small" aria-hidden="true" />
          {{ $t('statistics.STATISTICS', 0) }}
        </div>
        <div class="statistics">
          <SportStatCard
            icon="calendar"
            :loading="loading"
            :total-value="totalWorkouts"
            :label="$t('workouts.WORKOUT', 0)"
          />
        </div>
        <div
          class="statistics-workouts-count"
          v-if="
            sportStatistics && sportStatistics.total_workouts < totalWorkouts
          "
        >
          {{
            $t('statistics.STATISTICS_ON_LAST_WORKOUTS', {
              count: sportStatistics.total_workouts,
            })
          }}
        </div>
        <div v-else class="statistics-workouts-count">
          {{ $t('statistics.STATISTICS_ON_ALL_WORKOUTS') }}
        </div>
        <div class="statistics">
          <SportStatCard
            icon="road"
            :loading="loading"
            :total-value="
              convertedDistance(sportStatistics?.total_distance, 'km')
            "
            :text="distanceUnitTo"
            :label="$t('workouts.DISTANCE')"
          >
            <template #average>
              <div>{{ $t('statistics.AVERAGE') }}:</div>
              <Distance
                v-if="sportStatistics"
                :distance="sportStatistics.average_distance"
                unitFrom="km"
                :useImperialUnits="authUser.imperial_units"
              />
            </template>
          </SportStatCard>
          <SportStatCard
            icon="clock-o"
            :loading="loading"
            :total-value="totalDuration.days"
            :text="totalDuration.duration"
            :label="$t('workouts.DURATION')"
          >
            <template #average>
              <div>{{ $t('statistics.AVERAGE') }}:</div>
              <span>
                {{
                  sportStatistics
                    ? getTotalDuration(sportStatistics.average_duration, $t)
                    : ''
                }}
              </span>
            </template>
          </SportStatCard>
          <SportStatCard
            icon="tachometer"
            :loading="loading"
            :total-value="
              convertedDistance(sportStatistics?.average_speed, 'km')
            "
            :text="`${distanceUnitTo}/h`"
            :label="$t('workouts.AVE_SPEED')"
          />
          <SportStatCard
            v-if="sportStatistics?.total_ascent !== null"
            icon="location-arrow"
            :loading="loading"
            :total-value="convertedDistance(sportStatistics?.total_ascent, 'm')"
            :text="ascentUnitTo"
            :label="$t('workouts.ASCENT')"
          >
            <template #average>
              <div>{{ $t('statistics.AVERAGE') }}:</div>
              <Distance
                v-if="sportStatistics"
                :distance="sportStatistics.average_ascent"
                unitFrom="m"
                :useImperialUnits="authUser.imperial_units"
              />
            </template>
          </SportStatCard>
          <SportStatCard
            v-if="sportStatistics?.total_descent !== null"
            icon="location-arrow fa-rotate-90"
            :loading="loading"
            :total-value="
              convertedDistance(sportStatistics?.total_descent, 'm')
            "
            :text="ascentUnitTo"
            :label="$t('workouts.DESCENT')"
          >
            <template #average>
              <div>{{ $t('statistics.AVERAGE') }}:</div>
              <Distance
                v-if="sportStatistics"
                :distance="sportStatistics.average_descent"
                unitFrom="m"
                :useImperialUnits="authUser.imperial_units"
              />
            </template>
          </SportStatCard>
        </div>
      </div>
      <div class="records">
        <div class="label">
          <i class="fa fa-trophy custom-fa-small" aria-hidden="true" />
          {{ $t('workouts.RECORD', 0) }}
        </div>
        <div>
          <SportRecordsTable
            v-for="record in getTranslatedRecords(sportRecords)"
            :record="record"
            :key="record.id"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
  import { computed, onBeforeMount, toRefs, watch } from 'vue'
  import type { ComputedRef } from 'vue'
  import { useI18n } from 'vue-i18n'
  import { useRoute, useRouter } from 'vue-router'

  import SportRecordsTable from '@/components/Common/SportRecordsTable.vue'
  import SportStatCard from '@/components/Statistics/SportStatCard.vue'
  import { STATS_STORE } from '@/store/constants'
  import type { ISport, ITranslatedSport } from '@/types/sports'
  import type { TStatisticsForSport } from '@/types/statistics'
  import type { TUnit } from '@/types/units'
  import type { IAuthUserProfile } from '@/types/user'
  import type {
    ICardRecord,
    IDuration,
    IRecordsBySports,
  } from '@/types/workouts'
  import { useStore } from '@/use/useStore'
  import { getDuration, getTotalDuration } from '@/utils/duration'
  import { getRecordsBySports, sortRecords } from '@/utils/records'
  import { translateSports } from '@/utils/sports'
  import { convertDistance, units } from '@/utils/units'
  interface Props {
    sports: ISport[]
    authUser: IAuthUserProfile
  }
  const props = defineProps<Props>()
  const { authUser, sports } = toRefs(props)

  const route = useRoute()
  const router = useRouter()
  const store = useStore()
  const { t } = useI18n()

  const translatedSports: ComputedRef<ITranslatedSport[]> = computed(() =>
    translateSports(sports.value, t, 'all')
  )
  const sportIds: ComputedRef<number[]> = computed(() =>
    translatedSports.value.map((s) => s.id)
  )
  const sportId: ComputedRef<number> = computed(() =>
    route.query.sport_id &&
    sportIds.value.includes(+route.query.sport_id as number)
      ? +route.query.sport_id
      : sportIds.value[0]
  )
  const sportRecords: ComputedRef<IRecordsBySports> = computed(() =>
    getRecordsBySports(
      authUser.value.records,
      translatedSports.value,
      authUser.value.timezone,
      authUser.value.imperial_units,
      authUser.value.display_ascent,
      authUser.value.date_format,
      sportId.value
    )
  )
  const selectedSport: ComputedRef<ITranslatedSport | undefined> = computed(
    () => translatedSports.value.find((s) => s.id === sportId.value)
  )
  const sportStatistics: ComputedRef<TStatisticsForSport | null> = computed(
    () => store.getters.USER_SPORT_STATS[sportId.value]
  )
  const totalWorkouts: ComputedRef<number> = computed(
    () => store.getters.TOTAL_WORKOUTS
  )
  const distanceUnitTo: ComputedRef<TUnit> = computed(() =>
    authUser.value.imperial_units ? units['km'].defaultTarget : 'km'
  )
  const ascentUnitTo: ComputedRef<TUnit> = computed(() =>
    authUser.value.imperial_units ? units['m'].defaultTarget : 'm'
  )
  const loading: ComputedRef<boolean> = computed(
    () => store.getters.STATS_LOADING
  )
  const totalDuration: ComputedRef<IDuration> = computed(() =>
    sportStatistics.value
      ? getDuration(sportStatistics.value.total_duration, t)
      : { days: '', duration: '' }
  )

  function convertedDistance(
    value: number | undefined,
    unitFrom: TUnit
  ): number | string {
    if (value === undefined) {
      return ''
    }
    const unitTo = authUser.value.imperial_units
      ? units[unitFrom].defaultTarget
      : unitFrom
    return authUser.value.imperial_units
      ? convertDistance(value, unitFrom, unitTo, 2)
      : value
  }
  function getSportsStatistics() {
    store.dispatch(STATS_STORE.ACTIONS.GET_USER_SPORT_STATS, {
      username: authUser.value.username,
      sportId: sportId.value,
    })
  }
  function getTranslatedRecords(record: IRecordsBySports): ICardRecord[] {
    const translatedRecords: ICardRecord[] = []
    if (selectedSport.value?.translatedLabel) {
      record[selectedSport.value?.translatedLabel].records.map((record) => {
        translatedRecords.push({
          ...record,
          label: t(`workouts.RECORD_${record.record_type}`),
        })
      })
    }
    return translatedRecords.sort(sortRecords)
  }
  function updateParams(e: Event) {
    router.push({
      path: '/statistics',
      query: {
        chart: 'by_sport',
        sport_id: (e.target as HTMLSelectElement).value,
      },
    })
  }

  watch(
    () => route.query,
    () => {
      getSportsStatistics()
    }
  )

  onBeforeMount(() => getSportsStatistics())
</script>

<style scoped lang="scss">
  @use '~@/scss/vars.scss' as *;
  #sport-statistics {
    #sport {
      height: 30px;
      margin-left: $default-margin;
      padding: $default-padding * 0.5;
    }

    .label {
      font-weight: bold;
      text-transform: capitalize;
      margin: $default-margin * 2 0 $default-margin;
    }

    .statistics-workouts-count {
      font-style: italic;
    }
    .sport-statistics {
      .sport-img-label {
        display: flex;
        gap: $default-padding;
        align-items: flex-end;
        margin-top: $default-margin * 1.5;
        .sport-img {
          height: 50px;
          width: 50px;
        }
        .sport-label {
          font-size: 25px;
          font-weight: bold;
        }
      }
      .statistics {
        display: flex;
        justify-content: flex-start;
        flex-wrap: wrap;
      }
    }
    .records {
      width: 425px;
    }

    @media screen and (max-width: $x-small-limit) {
      .sport-statistics {
        .sport-img-label {
          .sport-img {
            height: 50px;
            width: 50px;
          }
          .sport-label {
            font-size: 20px;
            font-weight: bold;
          }
        }
        .records {
          font-size: 0.9em;
          width: 100%;
        }
      }
    }
  }
</style>
