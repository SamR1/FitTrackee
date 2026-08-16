<template>
  <div id="workout-sports-stats">
    <div class="all-sports">
      <WorkoutSegmentsSportsStatsTable
        :stats-with-sport="statsWithSport"
        :display-options="displayOptions"
      />
    </div>
    <div
      class="by-sport responsive-table"
      v-for="stats in statsWithSport"
      :key="stats.sport_id"
    >
      <WorkoutSegmentsSportsStatsTable
        :stats-with-sport="[stats]"
        :display-options="displayOptions"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
  import { computed, type ComputedRef, toRefs } from 'vue'

  import WorkoutSegmentsSportsStatsTable from '@/components/Workout/WorkoutDetail/WorkoutSegments/WorkoutSegmentsSportsStatsTable.vue'
  import useSports from '@/composables/useSports.ts'
  import { ROOT_STORE } from '@/store/constants.ts'
  import type { IDisplayOptions } from '@/types/application.ts'
  import type { IMultiSportsStats } from '@/types/workouts.ts'
  import { useStore } from '@/use/useStore.ts'
  interface Props {
    sportsStats: Record<number, IMultiSportsStats>
  }
  const props = defineProps<Props>()
  const { sportsStats } = toRefs(props)

  const store = useStore()

  const { getObjectSport } = useSports()

  const displayOptions: ComputedRef<IDisplayOptions> = computed(
    () => store.getters[ROOT_STORE.GETTERS.DISPLAY_OPTIONS]
  )
  const statsWithSport: ComputedRef<IMultiSportsStats[]> = computed(() =>
    Object.entries(sportsStats.value).map(([key, value]) => {
      return {
        ...value,
        sport: getObjectSport({ sport_id: +key }),
      }
    })
  )
</script>

<style scoped lang="scss">
  @use '~@/scss/vars.scss' as *;
  #workout-sports-stats {
    .all-sports {
      display: block;
    }
    .by-sport {
      display: none;
    }

    @media screen and (max-width: $x-small-limit) {
      .all-sports {
        display: none;
      }
      .by-sport {
        display: block;
      }
    }
  }
</style>
