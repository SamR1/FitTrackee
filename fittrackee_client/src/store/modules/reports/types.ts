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
  IReportActionPayload,
  IReportCommentPayload,
  IReportPayload,
  IGetReportPayload,
} from '@/types/reports'

export interface IReportsState {
  report: IReportForAdmin
  reports: IReportForAdmin[]
  pagination: IPagination
  reportStatus: string | null
  reportLoading: boolean
  reportUpdateLoading: boolean
}

export interface IReportsActions {
  [REPORTS_STORE.ACTIONS.EMPTY_REPORTS](
    context: ActionContext<IReportsState, IRootState>
  ): void
  [REPORTS_STORE.ACTIONS.GET_REPORT](
    context: ActionContext<IReportsState, IRootState>,
    reportPayload: IGetReportPayload
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
    payload: IReportActionPayload
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
  [REPORTS_STORE.GETTERS.REPORT_LOADING](state: IReportsState): boolean
  [REPORTS_STORE.GETTERS.REPORT_STATUS](state: IReportsState): string | null
  [REPORTS_STORE.GETTERS.REPORT_UPDATE_LOADING](state: IReportsState): boolean
  [REPORTS_STORE.GETTERS.REPORTS](state: IReportsState): IReport[]
  [REPORTS_STORE.GETTERS.REPORTS_PAGINATION](state: IReportsState): IPagination
}

export type TReportsMutations<S = IReportsState> = {
  [REPORTS_STORE.MUTATIONS.EMPTY_REPORT](state: S): void
  [REPORTS_STORE.MUTATIONS.SET_REPORT](state: S, report: IReport): void
  [REPORTS_STORE.MUTATIONS.SET_REPORT_LOADING](
    state: S,
    reportLoading: boolean
  ): void
  [REPORTS_STORE.MUTATIONS.SET_REPORT_UPDATE_LOADING](
    state: S,
    reportLoading: boolean
  ): void
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
