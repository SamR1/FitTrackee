import { computed, inject, reactive, ref } from 'vue'
import type { ComputedRef, Ref } from 'vue'

import { AUTH_USER_STORE, ROOT_STORE } from '@/store/constants'
import type { IEquipmentError } from '@/types/equipments'
import type {
  IAuthUserProfile,
  IUserSportPreferencesPayload,
} from '@/types/user'
import { useStore } from '@/use/useStore'
import { convertDistance } from '@/utils/units'

export default function useSport() {
  const store = useStore()

  const errorMessages: ComputedRef<string | string[] | IEquipmentError | null> =
    computed(() => store.getters[ROOT_STORE.GETTERS.ERROR_MESSAGES])
  const loading = computed(
    () => store.getters[AUTH_USER_STORE.GETTERS.USER_LOADING]
  )

  const defaultColor = '#838383'
  const sportColors = inject('sportColors') as Record<string, string>

  const displayModal: Ref<boolean> = ref(false)
  const defaultEquipmentId: Ref<string> = ref('')
  const sportPayload: IUserSportPreferencesPayload = reactive({
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

  return {
    defaultColor,
    defaultEquipmentId,
    displayModal,
    errorMessages,
    loading,
    sportColors,
    sportPayload,
    resetSport,
    updateDisplayModal,
    updateIsActive,
    updateSport,
  }
}
