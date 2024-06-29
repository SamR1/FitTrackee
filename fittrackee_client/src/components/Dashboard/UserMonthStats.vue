<template>
  <div class="user-month-stats">
    <div class="section-title">
      <i class="fa fa-calendar custom-fa-small" aria-hidden="true" />
      {{ $t('dashboard.THIS_MONTH') }}
    </div>
    <div class="box">
      <StatChart
        :sports="sports"
        :user="user"
        :chart-params="chartParams"
        :displayed-sport-ids="selectedSportIds"
        :hide-chart-if-no-data="true"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
  import { endOfMonth, startOfMonth } from 'date-fns'
  import { toRefs } from 'vue'

  import StatChart from '@/components/Common/StatsChart/index.vue'
  import type { ISport } from '@/types/sports'
  import type { IStatisticsDateParams } from '@/types/statistics'
  import type { IAuthUserProfile } from '@/types/user'

  interface Props {
    sports: ISport[]
    user: IAuthUserProfile
  }
  const props = defineProps<Props>()

  const { sports, user } = toRefs(props)
  const date = new Date()
  const chartParams: IStatisticsDateParams = {
    duration: 'week',
    start: startOfMonth(date),
    end: endOfMonth(date),
    statsType: 'total',
  }
  const selectedSportIds = sports.value.map((sport) => sport.id)
</script>

<style lang="scss" scoped>
  @import '~@/scss/vars.scss';

  .user-month-stats {
    ::v-deep(.card-content) {
      padding: $default-padding;
    }
  }
</style>
