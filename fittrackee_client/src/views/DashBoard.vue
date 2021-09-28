<template>
  <div id="dashboard" v-if="authUser.username && sports.length > 0">
    <div class="container">
      <UserStatsCards :user="authUser" />
    </div>
    <div class="container dashboard-container">
      <div class="left-container dashboard-sub-container">
        <UserMonthStats :sports="sports" :user="authUser" />
        <UserRecords :sports="sports" :user="authUser" />
      </div>
      <div class="right-container dashboard-sub-container">
        <UserCalendar :sports="sports" :user="authUser" />
        <Timeline :sports="sports" :user="authUser" />
      </div>
    </div>
  </div>
</template>

<script lang="ts">
  import { computed, ComputedRef, defineComponent, onUnmounted } from 'vue'

  import Timeline from '@/components/Dashboard/Timeline/index.vue'
  import UserCalendar from '@/components/Dashboard/UserCalendar/index.vue'
  import UserMonthStats from '@/components/Dashboard/UserMonthStats.vue'
  import UserRecords from '@/components/Dashboard/UserRecords/index.vue'
  import UserStatsCards from '@/components/Dashboard/UserStatsCards/index.vue'
  import { SPORTS_STORE, USER_STORE, WORKOUTS_STORE } from '@/store/constants'
  import { ISport } from '@/types/sports'
  import { IAuthUserProfile } from '@/types/user'
  import { useStore } from '@/use/useStore'

  export default defineComponent({
    name: 'Dashboard',
    components: {
      Timeline,
      UserCalendar,
      UserMonthStats,
      UserRecords,
      UserStatsCards,
    },
    setup() {
      const store = useStore()
      const authUser: ComputedRef<IAuthUserProfile> = computed(
        () => store.getters[USER_STORE.GETTERS.AUTH_USER_PROFILE]
      )
      const sports: ComputedRef<ISport[]> = computed(
        () => store.getters[SPORTS_STORE.GETTERS.SPORTS]
      )
      onUnmounted(() => {
        store.commit(WORKOUTS_STORE.MUTATIONS.EMPTY_WORKOUTS)
      })
      return { authUser, sports }
    },
  })
</script>

<style lang="scss" scoped>
  @import '~@/scss/base';
  .dashboard-container {
    display: flex;
    flex-direction: row;
    padding-bottom: 30px;
    .dashboard-sub-container {
      display: flex;
      flex-direction: column;
    }
    .left-container {
      width: 32%;
    }
    .right-container {
      width: 68%;
    }
  }
  @media screen and (max-width: $small-limit) {
    .dashboard-container {
      display: flex;
      flex-direction: column;
      .left-container {
        width: 100%;
      }
      .right-container {
        width: 100%;
      }
    }
  }
</style>
