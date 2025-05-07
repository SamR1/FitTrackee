import { computed, inject, reactive, ref } from 'vue'
import type { Reactive, ComputedRef, Ref } from 'vue'
import { useI18n } from 'vue-i18n'

import { AUTH_USER_STORE, SPORTS_STORE } from '@/store/constants'
import type { ISport, ITranslatedSport } from '@/types/sports'
import type {
  IAuthUserProfile,
  IUserSportPreferencesPayload,
} from '@/types/user'
import type { IWorkout } from '@/types/workouts'
import { useStore } from '@/use/useStore'
import { translateSports } from '@/utils/sports'
import { convertDistance } from '@/utils/units'

export default function useSports() {
  const store = useStore()
  const { t } = useI18n()

  const sportColors = inject('sportColors') as Record<string, string>

  const defaultColor = '#838383'

  const displayModal: Ref<boolean> = ref(false)
  const defaultEquipmentId: Ref<string> = ref('')

  const sports: ComputedRef<ISport[]> = computed(
    () => store.getters[SPORTS_STORE.GETTERS.SPORTS]
  )
  const translatedSports: ComputedRef<ITranslatedSport[]> = computed(() =>
    translateSports(sports.value, t)
  )

  const sportPayload: Reactive<IUserSportPreferencesPayload> = reactive({
    sport_id: 0,
    color: null,
    is_active: true,
    stopped_speed_threshold: 1,
    fromSport: false,
  })

  function updateIsActive(event: Event) {
    sportPayload.is_active = (event.target as HTMLInputElement).checked
  }
  function updateDisplayModal(value: boolean) {
    displayModal.value = value
  }
  function updateSport(authUser: IAuthUserProfile) {
    const payload = { ...sportPayload }
    payload.stopped_speed_threshold = authUser.imperial_units
      ? convertDistance(sportPayload.stopped_speed_threshold, 'mi', 'km', 2)
      : sportPayload.stopped_speed_threshold
    store.dispatch(
      AUTH_USER_STORE.ACTIONS.UPDATE_USER_SPORT_PREFERENCES,
      payload
    )
  }
  function resetSport(sportId: number, fromSport = false) {
    store.dispatch(AUTH_USER_STORE.ACTIONS.RESET_USER_SPORT_PREFERENCES, {
      sportId,
      fromSport,
    })
  }
  function getWorkoutSport(workout: IWorkout | null): ISport | null {
    return workout
      ? sports.value.find((s) => s.id === workout.sport_id) || null
      : null
  }

  return {
    defaultColor,
    defaultEquipmentId,
    displayModal,
    sportColors,
    sportPayload,
    sports,
    translatedSports,
    getWorkoutSport,
    resetSport,
    updateDisplayModal,
    updateIsActive,
    updateSport,
  }
}
