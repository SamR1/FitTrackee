<template>
  <div
    id="workouts"
    v-if="authUser.username && translatedSports.length > 0"
    class="view items-list-view"
  >
    <div class="container items-list-container">
      <div class="filters-container" :class="{ hidden: hiddenFilters }">
        <WorkoutsFilters
          :translatedSports="translatedSports"
          :authUser="authUser"
          :displayPace="displayPace"
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
        <WorkoutsList
          :authUser="authUser"
          :displayPace="displayPace"
          :translatedSports="translatedSports"
          :workouts="workouts"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
  import { computed, ref } from 'vue'
  import type { ComputedRef } from 'vue'
  import { useI18n } from 'vue-i18n'

  import WorkoutsFilters from '@/components/Workouts/WorkoutsFilters.vue'
  import WorkoutsList from '@/components/Workouts/WorkoutsList.vue'
  import {
    AUTH_USER_STORE,
    SPORTS_STORE,
    WORKOUTS_STORE,
  } from '@/store/constants'
  import type { ISport, ITranslatedSport } from '@/types/sports'
  import type { IAuthUserProfile } from '@/types/user'
  import type { IWorkout } from '@/types/workouts.ts'
  import { useStore } from '@/use/useStore'
  import { getDisplayPace, translateSports } from '@/utils/sports'

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

  const workouts: ComputedRef<IWorkout[]> = computed(
    () => store.getters[WORKOUTS_STORE.GETTERS.AUTH_USER_WORKOUTS]
  )
  const displayPace: ComputedRef<boolean> = computed(() => {
    const sport_ids = [...new Set(workouts.value.map((w) => w.sport_id))]
    if (sport_ids.length === 0) {
      return false
    }
    if (sport_ids.length === 1) {
      return getDisplayPace(sport_ids[0], translatedSports.value)
    }
    return translatedSports.value
      .filter((s) => sport_ids.includes(s.id))
      .every(
        (s) => s.pace_speed_display && s.pace_speed_display.startsWith('pace')
      )
  })

  function toggleFilters() {
    hiddenFilters.value = !hiddenFilters.value
  }
</script>
