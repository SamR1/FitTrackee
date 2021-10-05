<template>
  <div id="user-statistics" v-if="translatedSports">
    <StatsMenu
      @timeFrameUpdate="updateTimeFrame"
      @arrowClick="handleOnClickArrows"
    />
    <StatChart
      :sports="sports"
      :user="user"
      :chartParams="chartParams"
      :displayed-sport-ids="selectedSportIds"
      :fullStats="true"
    />
    <SportsMenu
      :selected-sport-ids="selectedSportIds"
      :user-sports="sports"
      @selectedSportIdsUpdate="updateSelectedSportIds"
    />
  </div>
</template>

<script lang="ts">
  import {
    ComputedRef,
    PropType,
    Ref,
    computed,
    defineComponent,
    ref,
    watch,
  } from 'vue'
  import { useI18n } from 'vue-i18n'

  import StatChart from '@/components/Common/StatsChart/index.vue'
  import SportsMenu from '@/components/Statistics/SportsMenu.vue'
  import StatsMenu from '@/components/Statistics/StatsMenu.vue'
  import { ISport, ITranslatedSport } from '@/types/sports'
  import { IStatisticsDateParams } from '@/types/statistics'
  import { IAuthUserProfile } from '@/types/user'
  import { translateSports, sportColors } from '@/utils/sports'
  import { getStatsDateParams, updateChartParams } from '@/utils/statistics'

  export default defineComponent({
    name: 'Statistics',
    components: {
      SportsMenu,
      StatChart,
      StatsMenu,
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
      const { t } = useI18n()
      let selectedTimeFrame = ref('month')
      const timeFrames = ['week', 'month', 'year']
      const chartParams: Ref<IStatisticsDateParams> = ref(
        getChartParams(selectedTimeFrame.value)
      )
      const translatedSports: ComputedRef<ITranslatedSport[]> = computed(() =>
        translateSports(props.sports, t)
      )
      const selectedSportIds: Ref<number[]> = ref(getSports(props.sports))

      function updateTimeFrame(timeFrame: string) {
        selectedTimeFrame.value = timeFrame
        chartParams.value = getChartParams(selectedTimeFrame.value)
      }
      function getChartParams(timeFrame: string): IStatisticsDateParams {
        return getStatsDateParams(new Date(), timeFrame, props.user.weekm)
      }
      function handleOnClickArrows(backward: boolean) {
        chartParams.value = updateChartParams(
          chartParams.value,
          backward,
          props.user.weekm
        )
      }
      function getSports(sports: ISport[]) {
        return sports.map((sport) => sport.id)
      }
      function updateSelectedSportIds(sportId: number) {
        if (selectedSportIds.value.includes(sportId)) {
          selectedSportIds.value = selectedSportIds.value.filter(
            (id) => id !== sportId
          )
        } else {
          selectedSportIds.value.push(sportId)
        }
      }

      watch(
        () => props.sports,
        (newSports) => {
          selectedSportIds.value = getSports(newSports)
        }
      )

      return {
        chartParams,
        selectedTimeFrame,
        sportColors,
        t,
        timeFrames,
        translatedSports,
        selectedSportIds,
        handleOnClickArrows,
        updateSelectedSportIds,
        updateTimeFrame,
      }
    },
  })
</script>

<style lang="scss" scoped>
  @import '~@/scss/base';

  #user-statistics {
    &.stats-disabled {
      opacity: 0.3;
      pointer-events: none;
    }

    ::v-deep(.chart-radio) {
      justify-content: space-around;
      padding: $default-padding * 3 $default-padding
        $default-padding$default-padding;
    }
  }
</style>
