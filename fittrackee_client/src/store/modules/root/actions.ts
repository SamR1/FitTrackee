import type { ActionContext, ActionTree } from 'vuex'

import authApi from '@/api/authApi'
import createI18n from '@/i18n'
import router from '@/router'
import { ROOT_STORE } from '@/store/constants'
import type { IRootActions, IRootState } from '@/store/modules/root/types'
import type { TAppConfigForm } from '@/types/application'
import type { TLanguage } from '@/types/locales'
import { handleError } from '@/utils'

const { locale } = createI18n.global

export const actions: ActionTree<IRootState, IRootState> & IRootActions = {
  [ROOT_STORE.ACTIONS.GET_APPLICATION_CONFIG](
    context: ActionContext<IRootState, IRootState>
  ): void {
    context.commit(ROOT_STORE.MUTATIONS.EMPTY_ERROR_MESSAGES)
    context.commit(ROOT_STORE.MUTATIONS.UPDATE_APPLICATION_LOADING, true)
    authApi
      .get('config')
      .then((res) => {
        if (res.data.status === 'success') {
          context.commit(
            ROOT_STORE.MUTATIONS.UPDATE_APPLICATION_CONFIG,
            res.data.data
          )
        } else {
          handleError(context, null)
        }
      })
      .catch((error) => handleError(context, error))
      .finally(() =>
        context.commit(ROOT_STORE.MUTATIONS.UPDATE_APPLICATION_LOADING, false)
      )
  },
  [ROOT_STORE.ACTIONS.GET_APPLICATION_STATS](
    context: ActionContext<IRootState, IRootState>
  ): void {
    context.commit(ROOT_STORE.MUTATIONS.EMPTY_ERROR_MESSAGES)
    authApi
      .get('stats/all')
      .then((res) => {
        if (res.data.status === 'success') {
          context.commit(
            ROOT_STORE.MUTATIONS.UPDATE_APPLICATION_STATS,
            res.data.data
          )
        } else {
          handleError(context, null)
        }
      })
      .catch((error) => handleError(context, error))
  },
  [ROOT_STORE.ACTIONS.GET_APPLICATION_PRIVACY_POLICY](
    context: ActionContext<IRootState, IRootState>
  ): void {
    context.commit(ROOT_STORE.MUTATIONS.EMPTY_ERROR_MESSAGES)
    authApi
      .get('config')
      .then((res) => {
        if (res.data.status === 'success') {
          context.commit(
            ROOT_STORE.MUTATIONS.UPDATE_APPLICATION_PRIVACY_POLICY,
            res.data.data
          )
        } else {
          handleError(context, null)
        }
      })
      .catch((error) => handleError(context, error))
  },
  [ROOT_STORE.ACTIONS.UPDATE_APPLICATION_CONFIG](
    context: ActionContext<IRootState, IRootState>,
    payload: TAppConfigForm
  ): void {
    context.commit(ROOT_STORE.MUTATIONS.EMPTY_ERROR_MESSAGES)
    authApi
      .patch('config', payload)
      .then((res) => {
        if (res.data.status === 'success') {
          context.commit(
            ROOT_STORE.MUTATIONS.UPDATE_APPLICATION_CONFIG,
            res.data.data
          )
          router.push('/admin/application')
        } else {
          handleError(context, null)
        }
      })
      .catch((error) => handleError(context, error))
  },
  [ROOT_STORE.ACTIONS.UPDATE_APPLICATION_LANGUAGE](
    context: ActionContext<IRootState, IRootState>,
    language: TLanguage
  ): void {
    document.querySelector('html')?.setAttribute('lang', language)
    context.commit(ROOT_STORE.MUTATIONS.UPDATE_LANG, language)
    locale.value = language
  },
}
