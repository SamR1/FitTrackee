<template>
  <div class="user-month-stats">
    <Card>
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
  import { endOfMonth, format, startOfMonth } from 'date-fns'
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
  import { STATS_STORE } from '@/store/constants'
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
      sports: {
        type: Object as PropType<ISport[]>,
        required: true,
      },
      user: {
        type: Object as PropType<IAuthUserProfile>,
        required: true,
      },
    },
    setup(props) {
      const store = useStore()
      const { t } = useI18n()

      onBeforeMount(() => getStatistics())

      const date = new Date()
      const dateFormat = 'yyyy-MM-dd'
      let displayedData = ref('total_distance')
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

      return {
        weekStartingMonday: computed<boolean>(() => props.user.weekm),
        chartParams,
        displayedData,
        statistics,
        t,
        updateDisplayData,
      }
    },
  })
</script>

<style lang="scss" scoped>
  @import '~@/scss/base';

  .user-month-stats {
    ::v-deep(.card-content) {
      padding: $default-padding;
      .stat-chart {
        .chart {
          .bar-chart {
            height: 100%;
          }
        }
      }
      .chart-radio {
        display: flex;
        justify-content: space-between;
        padding: $default-padding;

        label {
          font-size: 0.85em;
          font-weight: normal;
        }
      }
    }
  }
</style>
