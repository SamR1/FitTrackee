import { ActionContext, ActionTree } from 'vuex'
import { USER_STORE } from '@/store/constants'
import { IUserActions } from '@/store/modules/user/interfaces'
import { IUserState } from '@/store/modules/user/interfaces'
import { IRootState } from '@/store/modules/root/interfaces'
import { ILoginOrRegisterData } from '@/store/modules/user/interfaces'
import api from '@/api/defaultApi'
import authApi from '@/api/authApi'
import router from '@/router'

export const actions: ActionTree<IUserState, IRootState> & IUserActions = {
  [USER_STORE.ACTIONS.GET_USER_PROFILE](
    context: ActionContext<IUserState, IRootState>
  ): void {
    authApi
      .get('auth/profile')
      .then((res) => {
        if (res.data.status === 'success') {
          context.commit(
            USER_STORE.MUTATIONS.UPDATE_AUTH_USER_PROFILE,
            res.data.data
          )
        }
      })
      .catch((err) => console.log(err))
  },
  [USER_STORE.ACTIONS.LOGIN_OR_REGISTER](
    context: ActionContext<IUserState, IRootState>,
    data: ILoginOrRegisterData
  ): void {
    api
      .post(`/auth/${data.actionType}`, data.formData)
      .then((res) => {
        if (res.status == 200 && res.data.status === 'success') {
          const token = res.data.auth_token
          window.localStorage.setItem('authToken', token)
          context.commit(USER_STORE.MUTATIONS.UPDATE_AUTH_TOKEN, token)
          context
            .dispatch(USER_STORE.ACTIONS.GET_USER_PROFILE)
            .then(() => router.push('/'))
        }
      })
      .catch((err) => console.log(err))
  },
}
