import {
  ActionContext,
  CommitOptions,
  DispatchOptions,
  Store as VuexStore,
} from 'vuex'

import { WORKOUTS_STORE } from '@/store/constants'
import { IRootState } from '@/store/modules/root/types'
import { IWorkout, IWorkoutsPayload } from '@/types/workouts'

export interface IWorkoutsState {
  user_workouts: IWorkout[]
  calendar_workouts: IWorkout[]
}

export interface IWorkoutsActions {
  [WORKOUTS_STORE.ACTIONS.GET_CALENDAR_WORKOUTS](
    context: ActionContext<IWorkoutsState, IRootState>,
    payload: IWorkoutsPayload
  ): void
}

export interface IWorkoutsGetters {
  [WORKOUTS_STORE.GETTERS.CALENDAR_WORKOUTS](state: IWorkoutsState): IWorkout[]
}

export type TWorkoutsMutations<S = IWorkoutsState> = {
  [WORKOUTS_STORE.MUTATIONS.SET_CALENDAR_WORKOUTS](
    state: S,
    workouts: IWorkout[]
  ): void
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
