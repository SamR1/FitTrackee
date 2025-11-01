import { isBefore, subDays } from 'date-fns'
import { computed, type ComputedRef } from 'vue'

import { AUTH_USER_STORE } from '@/store/constants.ts'
import type { IExportRequest } from '@/types/user.ts'
import { useStore } from '@/use/useStore.ts'

export default function useUserDataExport() {
  const store = useStore()

  const exportRequest: ComputedRef<IExportRequest | null> = computed(
    () => store.getters[AUTH_USER_STORE.GETTERS.EXPORT_REQUEST]
  )

  function canRequestExport() {
    return exportRequest.value?.created_at
      ? isBefore(
          new Date(exportRequest.value.created_at),
          subDays(new Date(), 1)
        )
      : true
  }
  function requestExport() {
    store.dispatch(AUTH_USER_STORE.ACTIONS.REQUEST_DATA_EXPORT)
  }

  return {
    requestExport,
    canRequestExport,
  }
}
