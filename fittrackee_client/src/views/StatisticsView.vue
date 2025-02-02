<template>
  <div id="statistics" class="view">
    <div class="container" v-if="authUser.username">
      <Card>
        <template #title>
          {{ $t('statistics.STATISTICS') }}
          <label class="visually-hidden" for="stats-type">
            {{ $t('statistics.STATISTICS_TYPE') }}
          </label>
          <select
            v-if="userSports.length > 0"
            class="stats-types"
            name="stats-type"
            id="stats-type"
            v-model="selectedStatType"
            @change="updateParams"
          >
            <option
              v-for="statsType in statsTypes"
              :value="statsType"
              :key="statsType"
            >
              {{ $t(`statistics.STATISTICS_TYPES.${statsType}`) }}
            </option>
          </select>
        </template>
        <template #content>
          <Statistics
            v-if="$route.query.chart !== 'by_sport'"
            :class="{ 'stats-disabled': isDisabled }"
            :user="authUser"
            :sports="userSports"
            :isDisabled="isDisabled"
          />
          <SportStatistics
            v-else-if="userSports.length > 0"
            :sports="userSports"
            :authUser="authUser"
          />
        </template>
      </Card>
      <NoWorkouts v-if="authUser.nb_workouts === 0"></NoWorkouts>
    </div>
  </div>
</template>

<script setup lang="ts">
  import { computed, onBeforeMount, onMounted, ref } from 'vue'
  import type { ComputedRef, Ref } from 'vue'
  import { useRoute, useRouter } from 'vue-router'

  import Statistics from '@/components/Statistics/index.vue'
  import SportStatistics from '@/components/Statistics/SportStatistics.vue'
  import NoWorkouts from '@/components/Workouts/NoWorkouts.vue'
  import useAuthUser from '@/composables/useAuthUser'
  import useSports from '@/composables/useSports'
  import type { ISport } from '@/types/sports'
  import type { TStatisticsTypes } from '@/types/statistics'

  const route = useRoute()
  const router = useRouter()

  const { authUser } = useAuthUser()
  const { sports } = useSports()

  const statsTypes: TStatisticsTypes[] = ['by_time', 'by_sport']

  const selectedStatType: Ref<TStatisticsTypes> = ref('by_time')

  const userSports: ComputedRef<ISport[]> = computed(() =>
    sports.value.filter((sport) =>
      authUser.value.sports_list.includes(sport.id)
    )
  )
  const isDisabled: ComputedRef<boolean> = computed(
    () => authUser.value.nb_workouts === 0
  )

  function updateParams(e: Event) {
    router.push({
      path: '/statistics',
      query: { chart: (e.target as HTMLSelectElement).value },
    })
  }

  onBeforeMount(() => {
    selectedStatType.value =
      route.query.chart &&
      statsTypes.includes(route.query.chart as TStatisticsTypes)
        ? (route.query.chart as TStatisticsTypes)
        : 'by_time'
  })
  onMounted(() => {
    if (!isDisabled.value) {
      const select = document.getElementById('stats-type')
      select?.focus()
    }
  })
</script>

<style lang="scss" scoped>
  @use '~@/scss/vars.scss' as *;
  #statistics {
    display: flex;
    width: 100%;
    .container {
      display: flex;
      flex-direction: column;
      width: 100%;
    }
    .stats-types {
      height: 30px;
      margin-left: $default-margin;
      padding: $default-padding * 0.5;
    }
  }
</style>
