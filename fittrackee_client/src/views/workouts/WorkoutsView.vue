<template>
  <div id="workouts" v-if="authUser.username" class="view items-list-view">
    <div class="container items-list-container">
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
  import { IAuthUserProfile } from '@/types/user'
  import { useStore } from '@/use/useStore'
  import { translateSports } from '@/utils/sports'

  const { t } = useI18n()
  const store = useStore()

  const authUser: ComputedRef<IAuthUserProfile> = computed(
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
