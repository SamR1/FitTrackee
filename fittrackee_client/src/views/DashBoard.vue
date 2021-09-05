<template>
  <div id="dashboard" v-if="authUser.username">
    <div class="container">
      <UserStats :user="authUser" />
    </div>
    <div class="container dashboard-container">
      <div class="left-container dashboard-sub-container">
        <UserMonthStats :user="authUser" />
        <UserRecords />
      </div>
      <div class="right-container dashboard-sub-container">
        <UserCalendar :user="authUser" />
        <Timeline />
      </div>
    </div>
  </div>
</template>

<script lang="ts">
  import { computed, ComputedRef, defineComponent } from 'vue'

  import Timeline from '@/components/Dashboard/Timeline.vue'
  import UserCalendar from '@/components/Dashboard/UserCalendar/index.vue'
  import UserMonthStats from '@/components/Dashboard/UserMonthStats.vue'
  import UserRecords from '@/components/Dashboard/UserRecords.vue'
  import UserStats from '@/components/Dashboard/UserStats.vue'
  import { USER_STORE } from '@/store/constants'
  import { IAuthUserProfile } from '@/types/user'
  import { useStore } from '@/use/useStore'

  export default defineComponent({
    name: 'Dashboard',
    components: {
      Timeline,
      UserCalendar,
      UserMonthStats,
      UserRecords,
      UserStats,
    },
    setup() {
      const store = useStore()
      const authUser: ComputedRef<IAuthUserProfile> = computed(
        () => store.getters[USER_STORE.GETTERS.AUTH_USER_PROFILE]
      )
      return { authUser }
    },
  })
</script>

<style lang="scss">
  @import '~@/scss/base';
  .dashboard-container {
    display: flex;
    flex-direction: row;
    .dashboard-sub-container {
      display: flex;
      flex-direction: column;
    }
    .left-container {
      width: 35%;
    }
    .right-container {
      width: 65%;
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
