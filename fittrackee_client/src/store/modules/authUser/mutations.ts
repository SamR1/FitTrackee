import type { MutationTree } from 'vuex'

import { AUTH_USER_STORE } from '@/store/constants'
import type {
  IAuthUserState,
  TAuthUserMutations,
} from '@/store/modules/authUser/types'
import type {
  IUserReportAction,
  IAuthUserProfile,
  IExportRequest,
  IUserProfile,
} from '@/types/user'

export const mutations: MutationTree<IAuthUserState> & TAuthUserMutations = {
  [AUTH_USER_STORE.MUTATIONS.CLEAR_AUTH_USER_TOKEN](state: IAuthUserState) {
    state.authToken = null
    state.authUserProfile = <IAuthUserProfile>{}
  },
  [AUTH_USER_STORE.MUTATIONS.UPDATE_AUTH_TOKEN](
    state: IAuthUserState,
    authToken: string
  ) {
    state.authToken = authToken
  },
  [AUTH_USER_STORE.MUTATIONS.UPDATE_AUTH_USER_PROFILE](
    state: IAuthUserState,
    authUserProfile: IAuthUserProfile
  ) {
    state.authUserProfile = authUserProfile
  },
  [AUTH_USER_STORE.MUTATIONS.UPDATE_IS_REGISTRATION_SUCCESS](
    state: IAuthUserState,
    isRegistrationSuccess: boolean
  ) {
    state.isRegistrationSuccess = isRegistrationSuccess
  },
  [AUTH_USER_STORE.MUTATIONS.UPDATE_IS_SUCCESS](
    state: IAuthUserState,
    isSuccess: boolean
  ) {
    state.isSuccess = isSuccess
  },
  [AUTH_USER_STORE.MUTATIONS.UPDATE_FOLLOW_REQUESTS](
    state: IAuthUserState,
    followRequests: IUserProfile[]
  ) {
    state.followRequests = followRequests
  },
  [AUTH_USER_STORE.MUTATIONS.UPDATE_USER_LOADING](
    state: IAuthUserState,
    loading: boolean
  ) {
    state.loading = loading
  },
  [AUTH_USER_STORE.MUTATIONS.SET_EXPORT_REQUEST](
    state: IAuthUserState,
    exportRequest: IExportRequest
  ) {
    state.exportRequest = exportRequest
  },
  [AUTH_USER_STORE.MUTATIONS.UPDATE_BLOCKED_USERS](
    state: IAuthUserState,
    blockedUsers: IUserProfile[]
  ) {
    state.blockedUsers = blockedUsers
  },
  [AUTH_USER_STORE.MUTATIONS.SET_ACCOUNT_SUSPENSION](
    state: IAuthUserState,
    accountSuspension: IUserReportAction
  ) {
    state.userReportAction = accountSuspension
  },
  [AUTH_USER_STORE.MUTATIONS.SET_USER_SANCTION](
    state: IAuthUserState,
    sanction: IUserReportAction
  ) {
    state.userReportAction = sanction
  },
}
