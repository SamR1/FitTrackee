<template>
  <div id="statistics" class="view">
    <div class="container" v-if="authUser.username">
      <Card>
        <template #title>{{ $t('statistics.STATISTICS') }}</template>
        <template #content>
          <Statistics
            :class="{ 'stats-disabled': authUser.nb_workouts === 0 }"
            :user="authUser"
            :sports="sports"
          />
        </template>
      </Card>
      <NoWorkouts v-if="authUser.nb_workouts === 0"></NoWorkouts>
    </div>
  </div>
</template>

<script setup lang="ts">
  import { ComputedRef, computed } from 'vue'

  import Statistics from '@/components/Statistics/index.vue'
  import NoWorkouts from '@/components/Workouts/NoWorkouts.vue'
  import { AUTH_USER_STORE, SPORTS_STORE } from '@/store/constants'
  import { ISport } from '@/types/sports'
  import { IUserProfile } from '@/types/user'
  import { useStore } from '@/use/useStore'

  const store = useStore()

  const authUser: ComputedRef<IUserProfile> = computed(
    () => store.getters[AUTH_USER_STORE.GETTERS.AUTH_USER_PROFILE]
  )
  const sports: ComputedRef<ISport[]> = computed(() =>
    store.getters[SPORTS_STORE.GETTERS.SPORTS].filter((sport) =>
      authUser.value.sports_list.includes(sport.id)
    )
  )
</script>

<style lang="scss" scoped>
  @import '~@/scss/base';
  #statistics {
    display: flex;
    width: 100%;
    .container {
      display: flex;
      flex-direction: column;
      width: 100%;
    }
  }
</style>
