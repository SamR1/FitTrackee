<template>
  <div id="sport-statistics">
    <label for="sport"> {{ $t('workouts.SPORT', 1) }}: </label>
    <select id="sport" v-model="sportId" @change="getSportsStatistics()">
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
            :total-value="sportStatistics ? sportStatistics.total_workouts : ''"
            :label="$t('workouts.WORKOUT', 0)"
          />
          <SportStatCard
            icon="road"
            :loading="loading"
            :total-value="sportStatistics ? sportStatistics.total_distance : ''"
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
            :total-value="sportStatistics ? sportStatistics.average_speed : ''"
            :text="`${distanceUnitTo}/h`"
            :label="$t('workouts.AVE_SPEED')"
          />
          <SportStatCard
            icon="location-arrow"
            :loading="loading"
            :total-value="sportStatistics ? sportStatistics.total_ascent : ''"
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
            icon="location-arrow fa-rotate-90"
            :loading="loading"
            :total-value="sportStatistics ? sportStatistics.total_descent : ''"
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
  import { computed, onBeforeMount, ref, toRefs } from 'vue'
  import type { ComputedRef, Ref } from 'vue'
  import { useI18n } from 'vue-i18n'

  import SportRecordsTable from '@/components/Common/SportRecordsTable.vue'
  import SportStatCard from '@/components/Statistics/SportStatCard.vue'
  import { STATS_STORE } from '@/store/constants'
  import type { ISport, ITranslatedSport } from '@/types/sports'
  import type { TStatisticsForSport } from '@/types/statistics'
  import type { TUnit } from '@/types/units'
  import type { IAuthUserProfile } from '@/types/user'
  import type { ICardRecord, IRecordsBySports } from '@/types/workouts'
  import { useStore } from '@/use/useStore'
  import { getDuration, getTotalDuration } from '@/utils/duration'
  import { getRecordsBySports, sortRecords } from '@/utils/records'
  import { translateSports } from '@/utils/sports'
  import { units } from '@/utils/units'
  interface Props {
    sports: ISport[]
    authUser: IAuthUserProfile
  }
  const props = defineProps<Props>()

  const store = useStore()
  const { t } = useI18n()

  const { authUser, sports } = toRefs(props)
  const translatedSports: ComputedRef<ITranslatedSport[]> = computed(() =>
    translateSports(sports.value, t, 'all')
  )
  const sportId: Ref<number> = ref(sports.value[0].id)
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
  const distanceUnitTo: TUnit = authUser.value.imperial_units
    ? units['km'].defaultTarget
    : 'km'
  const ascentUnitTo: TUnit = authUser.value.imperial_units
    ? units['m'].defaultTarget
    : 'm'
  const loading: ComputedRef<boolean> = computed(
    () => store.getters.STATS_LOADING
  )
  const totalDuration = computed(() =>
    sportStatistics.value
      ? getDuration(sportStatistics.value.total_duration, t)
      : { days: '', duration: '' }
  )

  onBeforeMount(() => getSportsStatistics())

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
</script>

<style scoped lang="scss">
  @import '~@/scss/vars.scss';
  #sport-statistics {
    #sport {
      height: 30px;
      margin-left: $default-margin;
      padding: $default-padding * 0.5;
    }

    .label {
      font-weight: bold;
      text-transform: capitalize;
      margin: $default-margin * 3 0 $default-margin * 1.5;
    }

    .sport-statistics {
      .sport-img-label {
        display: flex;
        gap: $default-padding;
        align-items: flex-end;
        margin-top: $default-margin * 2;
        .sport-img {
          height: 120px;
          width: 120px;
        }
        .sport-label {
          font-size: 25px;
          font-weight: bold;
        }
      }
      .statistics {
        display: flex;
        justify-content: space-around;
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
            height: 80px;
            width: 80px;
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
