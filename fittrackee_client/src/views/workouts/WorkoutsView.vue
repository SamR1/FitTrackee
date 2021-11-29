<template>
  <div id="workouts" v-if="authUser.username" class="view">
    <div class="container workouts-container">
      <div class="filters-container" :class="{ hidden: hiddenFilters }">
        <WorkoutsFilters
          :sports="translatedSports"
          :authUser="authUser"
          @filter="toggleFilters"
        />
      </div>
      <div class="display-filters">
        <div @click="toggleFilters">
          <i
            :class="`fa fa-caret-${hiddenFilters ? 'down' : 'up'}`"
            aria-hidden="true"
          />
          <span>
            {{ $t(`workouts.${hiddenFilters ? 'DISPLAY' : 'HIDE'}_FILTERS`) }}
          </span>
        </div>
      </div>
      <div class="list-container">
        <WorkoutsList :user="authUser" :sports="translatedSports" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
  import { ComputedRef, computed, ref } from 'vue'
  import { useI18n } from 'vue-i18n'

  import WorkoutsFilters from '@/components/Workouts/WorkoutsFilters.vue'
  import WorkoutsList from '@/components/Workouts/WorkoutsList.vue'
  import { AUTH_USER_STORE, SPORTS_STORE } from '@/store/constants'
  import { ISport, ITranslatedSport } from '@/types/sports'
  import { IUserProfile } from '@/types/user'
  import { useStore } from '@/use/useStore'
  import { translateSports } from '@/utils/sports'

  const { t } = useI18n()
  const store = useStore()

  const authUser: ComputedRef<IUserProfile> = computed(
    () => store.getters[AUTH_USER_STORE.GETTERS.AUTH_USER_PROFILE]
  )
  const sports: ComputedRef<ISport[]> = computed(
    () => store.getters[SPORTS_STORE.GETTERS.SPORTS]
  )
  const translatedSports: ComputedRef<ITranslatedSport[]> = computed(() =>
    translateSports(sports.value, t)
  )
  const hiddenFilters = ref(true)

  function toggleFilters() {
    hiddenFilters.value = !hiddenFilters.value
  }
</script>

<style lang="scss" scoped>
  @import '~@/scss/vars.scss';
  #workouts {
    height: 100%;

    .workouts-container {
      display: flex;
      flex-direction: row;
      @media screen and (max-width: $medium-limit) {
        flex-direction: column;
      }

      .filters-container,
      .list-container {
        display: flex;
        flex-direction: column;
      }

      .filters-container {
        width: 25%;
        @media screen and (max-width: $medium-limit) {
          width: 100%;

          @media screen and (max-width: $small-limit) {
            &.hidden {
              display: none;
            }
          }
        }
      }

      .display-filters {
        display: none;
        font-size: 0.8em;
        padding: 0 $default-padding * 2;

        span {
          cursor: pointer;
          font-weight: bold;
          padding-left: $default-padding * 0.5;
        }
        .fa {
          cursor: pointer;
        }

        @media screen and (max-width: $small-limit) {
          display: flex;
          justify-content: flex-end;
          align-items: center;
        }
      }

      .list-container {
        width: 75%;
        @media screen and (max-width: $medium-limit) {
          width: 100%;
        }
      }
    }
  }
</style>
