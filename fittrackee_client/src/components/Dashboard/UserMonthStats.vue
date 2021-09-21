<template>
  <div class="user-month-stats">
    <Card :without-title="false">
      <template #title>{{ $t('dashboard.THIS_MONTH') }}</template>
      <template #content>
        <div v-if="Object.keys(statistics).length === 0">
          {{ t('workouts.NO_WORKOUTS') }}
        </div>
        <div v-else>
          <div class="chart-radio">
            <label class="">
              <input
                type="radio"
                name="total_distance"
                :checked="displayedData === 'total_distance'"
                @click="updateDisplayData"
              />
              {{ t('workouts.DISTANCE') }}
            </label>
            <label class="">
              <input
                type="radio"
                name="total_duration"
                :checked="displayedData === 'total_duration'"
                @click="updateDisplayData"
              />
              {{ t('workouts.DURATION') }}
            </label>
            <label class="">
              <input
                type="radio"
                name="nb_workouts"
                :checked="displayedData === 'nb_workouts'"
                @click="updateDisplayData"
              />
              {{ t('workouts.WORKOUT', 2) }}
            </label>
          </div>
          <Chart
            :displayedData="displayedData"
            :params="chartParams"
            :statistics="statistics"
            :sports="sports"
            :week-starting-monday="weekStartingMonday"
            v-if="statistics && weekStartingMonday !== undefined"
          />
        </div>
      </template>
    </Card>
  </div>
</template>

<script lang="ts">
  import { startOfMonth, endOfMonth, format } from 'date-fns'
  import {
    ComputedRef,
    PropType,
    computed,
    defineComponent,
    ref,
    onBeforeMount,
  } from 'vue'
  import { useI18n } from 'vue-i18n'

  import Card from '@/components/Common/Card.vue'
  import Chart from '@/components/Common/StatsChart/index.vue'
  import { STATS_STORE, SPORTS_STORE, USER_STORE } from '@/store/constants'
  import { ISport } from '@/types/sports'
  import { IStatisticsDateParams, TStatisticsFromApi } from '@/types/statistics'
  import { IAuthUserProfile } from '@/types/user'
  import { useStore } from '@/use/useStore'

  export default defineComponent({
    name: 'UserMonthStats',
    components: {
      Card,
      Chart,
    },
    props: {
      user: {
        type: Object as PropType<IAuthUserProfile>,
        required: true,
      },
    },
    setup(props) {
      const store = useStore()
      const date = new Date()
      const { t } = useI18n()
      const dateFormat = 'yyyy-MM-dd'
      const chartParams: IStatisticsDateParams = {
        duration: 'week',
        start: startOfMonth(date),
        end: endOfMonth(date),
      }
      const apiParams = {
        from: format(chartParams.start, dateFormat),
        to: format(chartParams.end, dateFormat),
        time: `week${props.user.weekm ? 'm' : ''}`,
      }
      const statistics: ComputedRef<TStatisticsFromApi> = computed(
        () => store.getters[STATS_STORE.GETTERS.USER_STATS]
      )
      const sports: ComputedRef<ISport[]> = computed(
        () => store.getters[SPORTS_STORE.GETTERS.SPORTS]
      )
      const authUser: ComputedRef<IAuthUserProfile> = computed(
        () => store.getters[USER_STORE.GETTERS.AUTH_USER_PROFILE]
      )
      let displayedData = ref('total_distance')

      function updateDisplayData(event: Event & { target: HTMLInputElement }) {
        displayedData.value = event.target.name
      }

      function getStatistics() {
        store.dispatch(STATS_STORE.ACTIONS.GET_USER_STATS, {
          username: props.user.username,
          filterType: 'by_time',
          params: apiParams,
        })
      }

      onBeforeMount(() => getStatistics())

      return {
        chartParams,
        displayedData,
        sports,
        statistics,
        t,
        updateDisplayData,
        weekStartingMonday: computed<boolean>(() => authUser.value.weekm),
      }
    },
  })
</script>

<style lang="scss" scoped>
  @import '~@/scss/base';

  .user-month-stats {
    ::v-deep(.stat-chart) {
      .chart {
        .bar-chart {
          height: 280px;
        }
        @media screen and (max-width: $small-limit) {
          .bar-chart {
            height: 100%;
          }
        }
      }
    }
    .chart-radio {
      display: flex;
      justify-content: space-between;
      padding: $default-padding;

      label {
        font-size: 0.9em;
        font-weight: normal;
      }
    }
  }
</style>
