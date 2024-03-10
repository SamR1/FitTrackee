import type {
  ActionContext,
  CommitOptions,
  DispatchOptions,
  Store as VuexStore,
} from 'vuex'

import { REPORTS_STORE } from '@/store/constants'
import type { IRootState } from '@/store/modules/root/types'
import type { IPagination, TPaginationPayload } from '@/types/api'
import type {
  IAppealPayload,
  IReportForAdmin,
  IReport,
  IReportAdminActionPayload,
  IReportCommentPayload,
  IReportPayload,
} from '@/types/reports'

export interface IReportsState {
  report: IReportForAdmin
  reports: IReportForAdmin[]
  pagination: IPagination
  reportStatus: string | null
}

export interface IReportsActions {
  [REPORTS_STORE.ACTIONS.EMPTY_REPORTS](
    context: ActionContext<IReportsState, IRootState>
  ): void
  [REPORTS_STORE.ACTIONS.GET_REPORT](
    context: ActionContext<IReportsState, IRootState>,
    reportId: number
  ): void
  [REPORTS_STORE.ACTIONS.GET_REPORTS](
    context: ActionContext<IReportsState, IRootState>,
    payload: TPaginationPayload
  ): void
  [REPORTS_STORE.ACTIONS.PROCESS_APPEAL](
    context: ActionContext<IReportsState, IRootState>,
    payload: IAppealPayload
  ): void
  [REPORTS_STORE.ACTIONS.SUBMIT_ADMIN_ACTION](
    context: ActionContext<IReportsState, IRootState>,
    payload: IReportAdminActionPayload
  ): void
  [REPORTS_STORE.ACTIONS.SUBMIT_REPORT](
    context: ActionContext<IReportsState, IRootState>,
    payload: IReportPayload
  ): void
  [REPORTS_STORE.ACTIONS.UPDATE_REPORT](
    context: ActionContext<IReportsState, IRootState>,
    payload: IReportCommentPayload
  ): void
}

export interface IReportsGetters {
  [REPORTS_STORE.GETTERS.REPORT](state: IReportsState): IReportForAdmin
  [REPORTS_STORE.GETTERS.REPORTS](state: IReportsState): IReport[]
  [REPORTS_STORE.GETTERS.REPORTS_PAGINATION](state: IReportsState): IPagination
  [REPORTS_STORE.GETTERS.REPORT_STATUS](state: IReportsState): string | null
}

export type TReportsMutations<S = IReportsState> = {
  [REPORTS_STORE.MUTATIONS.EMPTY_REPORT](state: S): void
  [REPORTS_STORE.MUTATIONS.SET_REPORT](state: S, report: IReport): void
  [REPORTS_STORE.MUTATIONS.SET_REPORTS](state: S, reports: IReport[]): void
  [REPORTS_STORE.MUTATIONS.SET_REPORTS_PAGINATION](
    state: S,
    pagination: IPagination
  ): void
  [REPORTS_STORE.MUTATIONS.SET_REPORT_STATUS](
    state: S,
    reportStatus: string | null
  ): void
}

export type TReportsStoreModule<S = IReportsState> = Omit<
  VuexStore<S>,
  'commit' | 'getters' | 'dispatch'
> & {
  dispatch<K extends keyof IReportsActions>(
    key: K,
    payload?: Parameters<IReportsActions[K]>[1],
    options?: DispatchOptions
  ): ReturnType<IReportsActions[K]>
} & {
  getters: {
    [K in keyof IReportsGetters]: ReturnType<IReportsGetters[K]>
  }
} & {
  commit<
    K extends keyof TReportsMutations,
    P extends Parameters<TReportsMutations[K]>[1],
  >(
    key: K,
    payload?: P,
    options?: CommitOptions
  ): ReturnType<TReportsMutations[K]>
}
