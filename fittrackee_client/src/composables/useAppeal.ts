import { computed, type ComputedRef, ref, type Ref } from 'vue'

import { ROOT_STORE, WORKOUTS_STORE } from '@/store/constants'
import { useStore } from '@/use/useStore'

export default function useAppeal() {
  const store = useStore()

  const displayAppealForm: Ref<null | string> = ref(null)

  const success: ComputedRef<null | string> = computed(
    () => store.getters[WORKOUTS_STORE.GETTERS.SUCCESS]
  )
  const appealLoading: ComputedRef<null | string> = computed(
    () => store.getters[WORKOUTS_STORE.GETTERS.APPEAL_LOADING]
  )

  function submitAppeal(
    text: string,
    objectType: 'comment' | 'workout',
    objectId: string
  ) {
    store.dispatch(WORKOUTS_STORE.ACTIONS.MAKE_APPEAL, {
      objectType,
      objectId,
      text,
    })
  }
  function cancelAppeal() {
    displayAppealForm.value = null
    store.commit(ROOT_STORE.MUTATIONS.EMPTY_ERROR_MESSAGES)
  }

  return {
    appealLoading,
    displayAppealForm,
    success,
    submitAppeal,
    cancelAppeal,
  }
}
