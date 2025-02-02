<template>
  <div id="user-statistics" v-if="translatedSports">
    <StatsMenu
      @statsTypeUpdate="updateStatsType"
      @timeFrameUpdate="updateTimeFrame"
      @arrowClick="handleOnClickArrows"
      :isDisabled="isDisabled"
    />
    <StatChart
      :sports="sports"
      :user="user"
      :chartParams="chartParams"
      :displayed-sport-ids="selectedSportIds"
      :fullStats="true"
      :isDisabled="isDisabled"
      :selectedTimeFrame="selectedTimeFrame"
    />
    <SportsMenu
      :selected-sport-ids="selectedSportIds"
      :user-sports="sports"
      @selectedSportIdsUpdate="updateSelectedSportIds"
    />
  </div>
</template>

<script setup lang="ts">
  import { computed, ref, toRefs, watch } from 'vue'
  import type { ComputedRef, Ref } from 'vue'
  import { useI18n } from 'vue-i18n'

  import StatChart from '@/components/Common/StatsChart/index.vue'
  import StatsMenu from '@/components/Statistics/StatsMenu.vue'
  import SportsMenu from '@/components/Statistics/StatsSportsMenu.vue'
  import type { ISport, ITranslatedSport } from '@/types/sports'
  import type {
    IStatisticsDateParams,
    TStatisticsTimeFrame,
    TStatisticsType,
  } from '@/types/statistics'
  import type { IAuthUserProfile } from '@/types/user'
  import { translateSports } from '@/utils/sports'
  import { getStatsDateParams, updateChartParams } from '@/utils/statistics'

  interface Props {
    sports: ISport[]
    user: IAuthUserProfile
    isDisabled: boolean
  }
  const props = defineProps<Props>()
  const { sports, user } = toRefs(props)

  const { t } = useI18n()

  const selectedTimeFrame: Ref<TStatisticsTimeFrame> = ref('month')
  const selectedStatsType: Ref<TStatisticsType> = ref('total')
  const chartParams: Ref<IStatisticsDateParams> = ref(
    getChartParams(selectedTimeFrame.value, selectedStatsType.value)
  )
  const selectedSportIds: Ref<number[]> = ref(getSports(sports.value))

  const translatedSports: ComputedRef<ITranslatedSport[]> = computed(() =>
    translateSports(props.sports, t)
  )

  function updateTimeFrame(timeFrame: TStatisticsTimeFrame) {
    selectedTimeFrame.value = timeFrame
    chartParams.value = getChartParams(timeFrame, selectedStatsType.value)
  }
  function updateStatsType(statsType: TStatisticsType) {
    selectedStatsType.value = statsType
    chartParams.value = getChartParams(selectedTimeFrame.value, statsType)
  }
  function getChartParams(
    timeFrame: TStatisticsTimeFrame,
    statsType: TStatisticsType
  ): IStatisticsDateParams {
    return getStatsDateParams(
      new Date(),
      timeFrame,
      props.user.weekm,
      statsType
    )
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
</script>

<style lang="scss" scoped>
  @use '~@/scss/vars.scss' as *;

  #user-statistics {
    &.stats-disabled {
      opacity: 0.3;
      pointer-events: none;
    }

    ::v-deep(.chart-radio) {
      justify-content: space-around;
      padding: $default-padding $default-padding 0;
    }
  }
</style>
