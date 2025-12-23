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
          @filter="toggleFilters"
          @updateSportWithPace="updateSportWithPace"
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
          :user="authUser"
          :translatedSports="translatedSports"
          :sportWithPace="sportWithPace"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
  import { computed, ref, watch } from 'vue'
  import type { ComputedRef } from 'vue'
  import { useI18n } from 'vue-i18n'
  import { useRoute } from 'vue-router'

  import WorkoutsFilters from '@/components/Workouts/WorkoutsFilters.vue'
  import WorkoutsList from '@/components/Workouts/WorkoutsList.vue'
  import { AUTH_USER_STORE, SPORTS_STORE } from '@/store/constants'
  import type { ISport, ITranslatedSport } from '@/types/sports'
  import type { IAuthUserProfile } from '@/types/user'
  import { useStore } from '@/use/useStore'
  import { sportsWithPace, translateSports } from '@/utils/sports'

  const { t } = useI18n()
  const route = useRoute()
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
  const sportWithPace = ref(false)

  function toggleFilters() {
    hiddenFilters.value = !hiddenFilters.value
  }
  function updateSportWithPace(sportId: string | undefined) {
    if (sportId !== undefined && sportId !== '') {
      const selectedSport = translatedSports.value.find(
        (sport) => sport.id === +sportId
      )
      if (selectedSport && sportsWithPace.includes(selectedSport.label)) {
        sportWithPace.value = true
        return
      }
    }
    sportWithPace.value = false
  }

  watch(
    () => route.query,
    (newValue) => {
      updateSportWithPace(newValue.sport_id as string | undefined)
    }
  )
  watch(
    () => [...translatedSports.value],
    (newValue) => {
      if (newValue.length > 0) {
        updateSportWithPace(route.query.sport_id as string | undefined)
      }
    }
  )
</script>
