import type {
  ActionContext,
  CommitOptions,
  DispatchOptions,
  Store as VuexStore,
} from 'vuex'

import { WORKOUTS_STORE } from '@/store/constants'
import type { IRootState } from '@/store/modules/root/types'
import type { IPagination } from '@/types/api'
import type {
  IWorkout,
  IWorkoutApiChartData,
  TWorkoutsPayload,
  IWorkoutData,
  IWorkoutPayload,
  IWorkoutForm,
  IWorkoutContentPayload,
  IWorkoutContentType,
  IWorkoutContentEdition,
} from '@/types/workouts'

export interface IWorkoutsState {
  user_workouts: IWorkout[]
  calendar_workouts: IWorkout[]
  timeline_workouts: IWorkout[]
  workoutData: IWorkoutData
  pagination: IPagination
  workoutContent: IWorkoutContentEdition
}

export interface IWorkoutsActions {
  [WORKOUTS_STORE.ACTIONS.GET_CALENDAR_WORKOUTS](
    context: ActionContext<IWorkoutsState, IRootState>,
    payload: TWorkoutsPayload
  ): void
  [WORKOUTS_STORE.ACTIONS.GET_USER_WORKOUTS](
    context: ActionContext<IWorkoutsState, IRootState>,
    payload: TWorkoutsPayload
  ): void
  [WORKOUTS_STORE.ACTIONS.GET_TIMELINE_WORKOUTS](
    context: ActionContext<IWorkoutsState, IRootState>,
    payload: TWorkoutsPayload
  ): void
  [WORKOUTS_STORE.ACTIONS.GET_MORE_TIMELINE_WORKOUTS](
    context: ActionContext<IWorkoutsState, IRootState>,
    payload: TWorkoutsPayload
  ): void
  [WORKOUTS_STORE.ACTIONS.GET_WORKOUT_DATA](
    context: ActionContext<IWorkoutsState, IRootState>,
    payload: IWorkoutPayload
  ): void
  [WORKOUTS_STORE.ACTIONS.DELETE_WORKOUT](
    context: ActionContext<IWorkoutsState, IRootState>,
    payload: IWorkoutPayload
  ): void
  [WORKOUTS_STORE.ACTIONS.EDIT_WORKOUT](
    context: ActionContext<IWorkoutsState, IRootState>,
    payload: IWorkoutPayload
  ): void
  [WORKOUTS_STORE.ACTIONS.EDIT_WORKOUT_CONTENT](
    context: ActionContext<IWorkoutsState, IRootState>,
    payload: IWorkoutContentPayload
  ): void
  [WORKOUTS_STORE.ACTIONS.ADD_WORKOUT](
    context: ActionContext<IWorkoutsState, IRootState>,
    payload: IWorkoutForm
  ): void
  [WORKOUTS_STORE.ACTIONS.ADD_WORKOUT_WITHOUT_GPX](
    context: ActionContext<IWorkoutsState, IRootState>,
    payload: IWorkoutForm
  ): void
}

export interface IWorkoutsGetters {
  [WORKOUTS_STORE.GETTERS.CALENDAR_WORKOUTS](state: IWorkoutsState): IWorkout[]
  [WORKOUTS_STORE.GETTERS.TIMELINE_WORKOUTS](state: IWorkoutsState): IWorkout[]
  [WORKOUTS_STORE.GETTERS.USER_WORKOUTS](state: IWorkoutsState): IWorkout[]
  [WORKOUTS_STORE.GETTERS.WORKOUT_CONTENT_EDITION](
    state: IWorkoutsState
  ): IWorkoutContentEdition
  [WORKOUTS_STORE.GETTERS.WORKOUT_DATA](state: IWorkoutsState): IWorkoutData
  [WORKOUTS_STORE.GETTERS.WORKOUTS_PAGINATION](
    state: IWorkoutsState
  ): IPagination
}

export type TWorkoutsMutations<S = IWorkoutsState> = {
  [WORKOUTS_STORE.MUTATIONS.ADD_TIMELINE_WORKOUTS](
    state: S,
    workouts: IWorkout[]
  ): void
  [WORKOUTS_STORE.MUTATIONS.SET_CALENDAR_WORKOUTS](
    state: S,
    workouts: IWorkout[]
  ): void
  [WORKOUTS_STORE.MUTATIONS.SET_TIMELINE_WORKOUTS](
    state: S,
    workouts: IWorkout[]
  ): void
  [WORKOUTS_STORE.MUTATIONS.SET_USER_WORKOUTS](
    state: S,
    workouts: IWorkout[]
  ): void
  [WORKOUTS_STORE.MUTATIONS.SET_WORKOUT](state: S, workout: IWorkout): void
  [WORKOUTS_STORE.MUTATIONS.SET_WORKOUT_CHART_DATA](
    state: S,
    chartDate: IWorkoutApiChartData[]
  ): void
  [WORKOUTS_STORE.MUTATIONS.SET_WORKOUT_CONTENT](
    state: S,
    workout: IWorkout
  ): void
  [WORKOUTS_STORE.MUTATIONS.SET_WORKOUT_CONTENT_LOADING](
    state: S,
    loading: boolean
  ): void
  [WORKOUTS_STORE.MUTATIONS.SET_WORKOUT_CONTENT_TYPE](
    state: S,
    contentType: IWorkoutContentType | ''
  ): void
  [WORKOUTS_STORE.MUTATIONS.SET_WORKOUT_GPX](state: S, gpx: string): void
  [WORKOUTS_STORE.MUTATIONS.SET_WORKOUT_LOADING](
    state: S,
    loading: boolean
  ): void
  [WORKOUTS_STORE.MUTATIONS.SET_WORKOUTS_PAGINATION](
    state: S,
    pagination: IPagination
  ): void
  [WORKOUTS_STORE.MUTATIONS.EMPTY_CALENDAR_WORKOUTS](state: S): void
  [WORKOUTS_STORE.MUTATIONS.EMPTY_WORKOUTS](state: S): void
  [WORKOUTS_STORE.MUTATIONS.EMPTY_WORKOUT](state: S): void
}

export type TWorkoutsStoreModule<S = IWorkoutsState> = Omit<
  VuexStore<S>,
  'commit' | 'getters' | 'dispatch'
> & {
  dispatch<K extends keyof IWorkoutsActions>(
    key: K,
    payload?: Parameters<IWorkoutsActions[K]>[1],
    options?: DispatchOptions
  ): ReturnType<IWorkoutsActions[K]>
} & {
  getters: {
    [K in keyof IWorkoutsGetters]: ReturnType<IWorkoutsGetters[K]>
  }
} & {
  commit<
    K extends keyof TWorkoutsMutations,
    P extends Parameters<TWorkoutsMutations[K]>[1],
  >(
    key: K,
    payload?: P,
    options?: CommitOptions
  ): ReturnType<TWorkoutsMutations[K]>
}
