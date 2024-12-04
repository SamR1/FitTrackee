import { computed } from 'vue'
import type { ComputedRef } from 'vue'
import { useRoute } from 'vue-router'

import useApp from '@/composables/useApp'
import { AUTH_USER_STORE } from '@/store/constants'
import type { IAuthUserProfile, TToken } from '@/types/user'
import { useStore } from '@/use/useStore'
import { getDateFormat } from '@/utils/dates'

export default function useAuthUser() {
  const route = useRoute()
  const store = useStore()

  const { appLanguage } = useApp()

  const authUser: ComputedRef<IAuthUserProfile> = computed(
    () => store.getters[AUTH_USER_STORE.GETTERS.AUTH_USER_PROFILE]
  )
  const authUserLoading = computed(
    () => store.getters[AUTH_USER_STORE.GETTERS.USER_LOADING]
  )
  const authUserSuccess = computed(
    () => store.getters[AUTH_USER_STORE.GETTERS.IS_SUCCESS]
  )
  const dateFormat: ComputedRef<string> = computed(() =>
    getDateFormat(authUser.value.date_format, appLanguage.value)
  )
  const isAuthenticated: ComputedRef<boolean> = computed(
    () => store.getters[AUTH_USER_STORE.GETTERS.IS_AUTHENTICATED]
  )
  const authUserHasAdminRights: ComputedRef<boolean> = computed(
    () => store.getters[AUTH_USER_STORE.GETTERS.HAS_ADMIN_RIGHTS]
  )
  const authUserHasModeratorRights: ComputedRef<boolean> = computed(
    () => store.getters[AUTH_USER_STORE.GETTERS.HAS_MODERATOR_RIGHTS]
  )
  const authUserHasOwnerRights: ComputedRef<boolean> = computed(
    () => store.getters[AUTH_USER_STORE.GETTERS.HAS_OWNER_RIGHTS]
  )
  const isAuthUserSuspended: ComputedRef<boolean> = computed(
    () => store.getters[AUTH_USER_STORE.GETTERS.IS_SUSPENDED]
  )
  const imperialUnits: ComputedRef<boolean> = computed(
    () => authUser.value.imperial_units
  )
  const timezone: ComputedRef<string> = computed(() => getTimezone())
  const token: ComputedRef<TToken> = computed(() => route.query.token)

  function getTimezone() {
    return authUser.value.timezone
      ? authUser.value.timezone
      : Intl.DateTimeFormat().resolvedOptions().timeZone
        ? Intl.DateTimeFormat().resolvedOptions().timeZone
        : 'Europe/Paris'
  }

  return {
    authUser,
    authUserHasAdminRights,
    authUserHasModeratorRights,
    authUserHasOwnerRights,
    authUserLoading,
    authUserSuccess,
    dateFormat,
    imperialUnits,
    isAuthenticated,
    isAuthUserSuspended,
    timezone,
    token,
  }
}
