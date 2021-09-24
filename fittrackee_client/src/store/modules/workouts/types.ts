import {
  ActionContext,
  CommitOptions,
  DispatchOptions,
  Store as VuexStore,
} from 'vuex'

import { WORKOUTS_STORE } from '@/store/constants'
import { IRootState } from '@/store/modules/root/types'
import { IWorkout, IWorkoutsPayload, IWorkoutState } from '@/types/workouts'

export interface IWorkoutsState {
  user_workouts: IWorkout[]
  calendar_workouts: IWorkout[]
  workout: IWorkoutState
}

export interface IWorkoutsActions {
  [WORKOUTS_STORE.ACTIONS.GET_CALENDAR_WORKOUTS](
    context: ActionContext<IWorkoutsState, IRootState>,
    payload: IWorkoutsPayload
  ): void
  [WORKOUTS_STORE.ACTIONS.GET_USER_WORKOUTS](
    context: ActionContext<IWorkoutsState, IRootState>,
    payload: IWorkoutsPayload
  ): void
  [WORKOUTS_STORE.ACTIONS.GET_WORKOUT](
    context: ActionContext<IWorkoutsState, IRootState>,
    workoutId: string | string[]
  ): void
}

export interface IWorkoutsGetters {
  [WORKOUTS_STORE.GETTERS.CALENDAR_WORKOUTS](state: IWorkoutsState): IWorkout[]
  [WORKOUTS_STORE.GETTERS.USER_WORKOUTS](state: IWorkoutsState): IWorkout[]
  [WORKOUTS_STORE.GETTERS.WORKOUT](state: IWorkoutsState): IWorkoutState
}

export type TWorkoutsMutations<S = IWorkoutsState> = {
  [WORKOUTS_STORE.MUTATIONS.SET_CALENDAR_WORKOUTS](
    state: S,
    workouts: IWorkout[]
  ): void
  [WORKOUTS_STORE.MUTATIONS.SET_USER_WORKOUTS](
    state: S,
    workouts: IWorkout[]
  ): void
  [WORKOUTS_STORE.MUTATIONS.SET_WORKOUT](state: S, workout: IWorkout): void
  [WORKOUTS_STORE.MUTATIONS.SET_WORKOUT_GPX](state: S, gpx: string): void
  [WORKOUTS_STORE.MUTATIONS.SET_WORKOUT_LOADING](
    state: S,
    loading: boolean
  ): void
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
    P extends Parameters<TWorkoutsMutations[K]>[1]
  >(
    key: K,
    payload?: P,
    options?: CommitOptions
  ): ReturnType<TWorkoutsMutations[K]>
}
