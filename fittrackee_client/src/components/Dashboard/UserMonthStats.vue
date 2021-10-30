<template>
  <div class="user-month-stats">
    <Card>
      <template #title>{{ $t('dashboard.THIS_MONTH') }}</template>
      <template #content>
        <StatChart
          :sports="sports"
          :user="user"
          :chart-params="chartParams"
          :displayed-sport-ids="selectedSportIds"
          :hide-chart-if-no-data="true"
        />
      </template>
    </Card>
  </div>
</template>

<script lang="ts">
  import { endOfMonth, startOfMonth } from 'date-fns'
  import { PropType, defineComponent } from 'vue'

  import StatChart from '@/components/Common/StatsChart/index.vue'
  import { ISport } from '@/types/sports'
  import { IUserProfile } from '@/types/user'

  export default defineComponent({
    name: 'UserMonthStats',
    components: {
      StatChart,
    },
    props: {
      sports: {
        type: Object as PropType<ISport[]>,
        required: true,
      },
      user: {
        type: Object as PropType<IUserProfile>,
        required: true,
      },
    },
    setup(props) {
      const date = new Date()
      return {
        chartParams: {
          duration: 'week',
          start: startOfMonth(date),
          end: endOfMonth(date),
        },
        selectedSportIds: props.sports.map((sport) => sport.id),
      }
    },
  })
</script>

<style lang="scss" scoped>
  @import '~@/scss/base';

  .user-month-stats {
    ::v-deep(.card-content) {
      padding: $default-padding;
    }
  }
</style>
