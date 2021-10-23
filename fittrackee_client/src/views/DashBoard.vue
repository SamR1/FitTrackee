<template>
  <div id="dashboard" v-if="authUser.username && sports.length > 0">
    <div class="container mobile-menu">
      <div class="box">
        <div
          class="mobile-menu-item"
          :class="{ 'is-selected': isSelected === 'chart' }"
          @click="updateDisplayColumn('chart')"
        >
          <i class="fa fa-bar-chart" aria-hidden="true" />
        </div>
        <div
          class="mobile-menu-item"
          :class="{ 'is-selected': isSelected === 'calendar' }"
          @click="updateDisplayColumn('calendar')"
        >
          <i class="fa fa-calendar" aria-hidden="true" />
        </div>
        <div
          class="mobile-menu-item"
          :class="{ 'is-selected': isSelected === 'timeline' }"
          @click="updateDisplayColumn('timeline')"
        >
          <i class="fa fa-map-o" aria-hidden="true" />
        </div>
        <div
          class="mobile-menu-item"
          :class="{ 'is-selected': isSelected === 'records' }"
          @click="updateDisplayColumn('records')"
        >
          <i class="fa fa-trophy" aria-hidden="true" />
        </div>
      </div>
    </div>
    <div class="container">
      <UserStatsCards :user="authUser" />
    </div>
    <div class="container dashboard-container">
      <div class="left-container dashboard-sub-container">
        <UserMonthStats
          :sports="sports"
          :user="authUser"
          :class="{ 'is-hidden': !(isSelected === 'chart') }"
        />
        <UserRecords
          :sports="sports"
          :user="authUser"
          :class="{ 'is-hidden': !(isSelected === 'records') }"
        />
      </div>
      <div class="right-container dashboard-sub-container">
        <UserCalendar
          :sports="sports"
          :user="authUser"
          :class="{ 'is-hidden': !(isSelected === 'calendar') }"
        />
        <Timeline
          :sports="sports"
          :user="authUser"
          :class="{ 'is-hidden': !(isSelected === 'timeline') }"
        />
      </div>
    </div>
    <div id="bottom" />
  </div>
  <div v-else class="app-loading">
    <Loader />
  </div>
</template>

<script lang="ts">
  import {
    ComputedRef,
    Ref,
    computed,
    defineComponent,
    ref,
    onUnmounted,
  } from 'vue'

  import Timeline from '@/components/Dashboard/Timeline.vue'
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
      const isSelected: Ref<string> = ref('chart')
      onUnmounted(() => {
        store.commit(WORKOUTS_STORE.MUTATIONS.EMPTY_WORKOUTS)
      })

      function updateDisplayColumn(target: string) {
        isSelected.value = target
      }

      return { authUser, sports, isSelected, updateDisplayColumn }
    },
  })
</script>

<style lang="scss" scoped>
  @import '~@/scss/base';
  #dashboard {
    padding-bottom: 30px;
    .dashboard-container {
      display: flex;
      flex-direction: row;

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
    .mobile-menu {
      display: none;
    }

    @media screen and (max-width: $medium-limit) {
      padding-bottom: 60px;
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
      .mobile-menu {
        display: flex;
        .box {
          display: flex;
          justify-content: space-between;
          padding: 0;
          width: 100%;

          .mobile-menu-item {
            display: flex;
            justify-content: space-around;
            border: none;
            border-radius: $border-radius;
            box-shadow: none;
            font-size: 0.95em;
            padding: $default-padding;
            width: 25%;

            .fa-trophy {
              color: var(--app-color);
            }
            &.is-selected {
              .fa-trophy {
                color: var(--mobile-menu-selected-color);
              }
              color: var(--mobile-menu-selected-color);
              background-color: var(--mobile-menu-selected-bgcolor);
            }
          }
        }
      }
      .is-hidden {
        display: none;
      }
    }
  }
</style>
