import type { ActionContext, ActionTree } from 'vuex'

import authApi from '@/api/authApi'
import {
  REPORTS_STORE,
  ROOT_STORE,
  USERS_STORE,
  WORKOUTS_STORE,
} from '@/store/constants'
import type {
  IReportsState,
  IReportsActions,
} from '@/store/modules/reports/types'
import type { IRootState } from '@/store/modules/root/types'
import type { TPaginationPayload } from '@/types/api'
import type {
  IAppealPayload,
  IGetReportPayload,
  IReportActionPayload,
  IReportCommentPayload,
  IReportPayload,
} from '@/types/reports'
import { handleError } from '@/utils'

export const actions: ActionTree<IReportsState, IRootState> & IReportsActions =
  {
    [REPORTS_STORE.ACTIONS.EMPTY_REPORTS](
      context: ActionContext<IReportsState, IRootState>
    ): void {
      context.commit(ROOT_STORE.MUTATIONS.EMPTY_ERROR_MESSAGES)
      context.commit(REPORTS_STORE.MUTATIONS.EMPTY_REPORT)
      context.commit(REPORTS_STORE.MUTATIONS.SET_REPORTS, [])
      context.commit(REPORTS_STORE.MUTATIONS.SET_REPORTS_PAGINATION, {})
    },
    [REPORTS_STORE.ACTIONS.GET_REPORT](
      context: ActionContext<IReportsState, IRootState>,
      reportPayload: IGetReportPayload
    ): void {
      context.commit(ROOT_STORE.MUTATIONS.EMPTY_ERROR_MESSAGES)
      context.commit(
        REPORTS_STORE.MUTATIONS[`SET_${reportPayload.loader}_LOADING`],
        true
      )
      authApi
        .get(`reports/${reportPayload.reportId}`)
        .then((res) => {
          if (res.data.status === 'success') {
            context.commit(REPORTS_STORE.MUTATIONS.SET_REPORT, res.data.report)
          } else {
            handleError(context, null)
          }
        })
        .catch((error) => handleError(context, error))
        .finally(() =>
          context.commit(
            REPORTS_STORE.MUTATIONS[`SET_${reportPayload.loader}_LOADING`],
            false
          )
        )
    },
    [REPORTS_STORE.ACTIONS.GET_REPORTS](
      context: ActionContext<IReportsState, IRootState>,
      payload: TPaginationPayload
    ): void {
      context.commit(ROOT_STORE.MUTATIONS.EMPTY_ERROR_MESSAGES)
      authApi
        .get('reports', { params: payload })
        .then((res) => {
          if (res.data.status === 'success') {
            context.commit(
              REPORTS_STORE.MUTATIONS.SET_REPORTS,
              res.data.reports
            )
            context.commit(
              REPORTS_STORE.MUTATIONS.SET_REPORTS_PAGINATION,
              res.data.pagination
            )
          } else {
            handleError(context, null)
          }
        })
        .catch((error) => handleError(context, error))
    },
    [REPORTS_STORE.ACTIONS.PROCESS_APPEAL](
      context: ActionContext<IReportsState, IRootState>,
      payload: IAppealPayload
    ): void {
      context.commit(ROOT_STORE.MUTATIONS.EMPTY_ERROR_MESSAGES)
      const { appealId, reportId, ...data } = payload
      authApi
        .patch(`appeals/${appealId}`, data)
        .then((res) => {
          if (res.data.status === 'success') {
            context.dispatch(REPORTS_STORE.ACTIONS.GET_REPORT, {
              reportId: reportId,
              loader: 'REPORT_UPDATE',
            })
          } else {
            handleError(context, null)
          }
        })
        .catch((error) => {
          handleError(context, error)
        })
    },
    [REPORTS_STORE.ACTIONS.SUBMIT_ADMIN_ACTION](
      context: ActionContext<IReportsState, IRootState>,
      payload: IReportActionPayload
    ): void {
      context.commit(ROOT_STORE.MUTATIONS.EMPTY_ERROR_MESSAGES)
      context.commit(USERS_STORE.MUTATIONS.UPDATE_IS_SUCCESS, false)
      context.commit(REPORTS_STORE.MUTATIONS.SET_REPORT_UPDATE_LOADING, true)
      const { report_id, ...data } = payload
      authApi
        .post(`reports/${report_id}/actions`, data)
        .then((res) => {
          if (res.data.status === 'success') {
            context.commit(REPORTS_STORE.MUTATIONS.SET_REPORT, res.data.report)
            context.commit(USERS_STORE.MUTATIONS.UPDATE_IS_SUCCESS, true)
          } else {
            handleError(context, null)
          }
        })
        .catch((error) => {
          handleError(context, error)
        })
        .finally(() =>
          context.commit(
            REPORTS_STORE.MUTATIONS.SET_REPORT_UPDATE_LOADING,
            false
          )
        )
    },
    [REPORTS_STORE.ACTIONS.SUBMIT_REPORT](
      context: ActionContext<IReportsState, IRootState>,
      payload: IReportPayload
    ): void {
      context.commit(ROOT_STORE.MUTATIONS.EMPTY_ERROR_MESSAGES)
      context.commit(REPORTS_STORE.MUTATIONS.SET_REPORT_STATUS, 'loading')
      authApi
        .post('reports', payload)
        .then((res) => {
          if (res.data.status === 'created') {
            context.commit(
              REPORTS_STORE.MUTATIONS.SET_REPORT_STATUS,
              `${payload.object_type}-${payload.object_id}-created`
            )
            if (payload.object_type === 'comment') {
              context.commit(
                WORKOUTS_STORE.MUTATIONS.SET_CURRENT_COMMENT_EDITION,
                {}
              )
            }
            if (payload.object_type === 'workout') {
              context.commit(
                WORKOUTS_STORE.MUTATIONS.SET_CURRENT_REPORTING,
                false
              )
            }
            if (payload.object_type === 'user') {
              context.commit(
                USERS_STORE.MUTATIONS.UPDATE_USER_CURRENT_REPORTING,
                false
              )
            }
          } else {
            context.commit(REPORTS_STORE.MUTATIONS.SET_REPORT_STATUS, null)
            handleError(context, null)
          }
        })
        .catch((error) => {
          handleError(context, error)
          context.commit(REPORTS_STORE.MUTATIONS.SET_REPORT_STATUS, null)
        })
    },
    [REPORTS_STORE.ACTIONS.UPDATE_REPORT](
      context: ActionContext<IReportsState, IRootState>,
      payload: IReportCommentPayload
    ): void {
      context.commit(ROOT_STORE.MUTATIONS.EMPTY_ERROR_MESSAGES)
      context.commit(REPORTS_STORE.MUTATIONS.SET_REPORT_UPDATE_LOADING, true)
      const { reportId, ...data } = payload
      authApi
        .patch(`reports/${reportId}`, data)
        .then((res) => {
          if (res.data.status === 'success') {
            context.commit(REPORTS_STORE.MUTATIONS.SET_REPORT, res.data.report)
          } else {
            context.commit(REPORTS_STORE.MUTATIONS.SET_REPORT_STATUS, null)
            handleError(context, null)
          }
        })
        .catch((error) => {
          handleError(context, error)
          context.commit(REPORTS_STORE.MUTATIONS.SET_REPORT_STATUS, null)
        })
        .finally(() =>
          context.commit(
            REPORTS_STORE.MUTATIONS.SET_REPORT_UPDATE_LOADING,
            false
          )
        )
    },

    [REPORTS_STORE.ACTIONS.GET_UNRESOLVED_REPORTS_STATUS](
      context: ActionContext<IReportsState, IRootState>
    ): void {
      context.commit(ROOT_STORE.MUTATIONS.EMPTY_ERROR_MESSAGES)
      authApi
        .get('reports/unresolved')
        .then((res) => {
          if (res.data.status === 'success') {
            console.log(res.data)
            context.commit(
              REPORTS_STORE.MUTATIONS.SET_UNRESOLVED_REPORTS_STATUS,
              res.data.unresolved
            )
          } else {
            handleError(context, null)
          }
        })
        .catch((error) => handleError(context, error))
    },
  }
