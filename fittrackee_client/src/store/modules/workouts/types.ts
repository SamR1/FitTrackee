import type { GeoJSON } from 'geojson'
import type {
  ActionContext,
  CommitOptions,
  DispatchOptions,
  Store as VuexStore,
} from 'vuex'

import { WORKOUTS_STORE } from '@/store/constants'
import type { IRootState } from '@/store/modules/root/types'
import type { IPagination } from '@/types/api'
import type { IWorkoutsFeatureCollection } from '@/types/geojson.ts'
import type { IUserLightProfile } from '@/types/user.ts'
import type {
  ICommentForm,
  IWorkout,
  IWorkoutApiChartData,
  TWorkoutsPayload,
  IWorkoutData,
  IWorkoutPayload,
  IWorkoutForm,
  IComment,
  ICommentPayload,
  ICurrentCommentEdition,
  IAppealPayload,
  IWorkoutContentPayload,
  IWorkoutContentType,
  IWorkoutContentEdition,
  ILikesPayload,
  TWorkoutsStatistics,
  TWorkoutsMapPayload,
  IWorkoutElevationSourceDataPayload,
} from '@/types/workouts'

export interface IWorkoutsState {
  user_workouts: IWorkout[]
  user_workouts_collection: IWorkoutsFeatureCollection
  user_workouts_statistics: TWorkoutsStatistics
  calendar_workouts: IWorkout[]
  timeline_workouts: IWorkout[]
  workoutData: IWorkoutData
  pagination: IPagination
  workoutContent: IWorkoutContentEdition
  success: null | string
  appealLoading: null | string
  likes: IUserLightProfile[]
  geocodeLoading: boolean
  mapLoading: boolean
}

export interface IWorkoutsActions {
  [WORKOUTS_STORE.ACTIONS.GET_CALENDAR_WORKOUTS](
    context: ActionContext<IWorkoutsState, IRootState>,
    payload: TWorkoutsPayload
  ): void
  [WORKOUTS_STORE.ACTIONS.GET_AUTH_USER_WORKOUTS](
    context: ActionContext<IWorkoutsState, IRootState>,
    payload: TWorkoutsPayload
  ): void
  [WORKOUTS_STORE.ACTIONS.GET_AUTH_USER_WORKOUTS_COLLECTION](
    context: ActionContext<IWorkoutsState, IRootState>,
    payload: TWorkoutsPayload
  ): void
  [WORKOUTS_STORE.ACTIONS.GET_AUTH_USER_WORKOUTS_FOR_GLOBAl_MAP](
    context: ActionContext<IWorkoutsState, IRootState>,
    payload: TWorkoutsMapPayload
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
  [WORKOUTS_STORE.ACTIONS.ADD_WORKOUT_WITHOUT_FILE](
    context: ActionContext<IWorkoutsState, IRootState>,
    payload: IWorkoutForm
  ): void
  [WORKOUTS_STORE.ACTIONS.ADD_COMMENT](
    context: ActionContext<IWorkoutsState, IRootState>,
    payload: ICommentForm
  ): void
  [WORKOUTS_STORE.ACTIONS.GET_WORKOUT_COMMENTS](
    context: ActionContext<IWorkoutsState, IRootState>,
    workoutId: string
  ): void
  [WORKOUTS_STORE.ACTIONS.GET_WORKOUT_COMMENT](
    context: ActionContext<IWorkoutsState, IRootState>,
    commentId: string
  ): void
  [WORKOUTS_STORE.ACTIONS.DELETE_WORKOUT_COMMENT](
    context: ActionContext<IWorkoutsState, IRootState>,
    payload: ICommentPayload
  ): void
  [WORKOUTS_STORE.ACTIONS.EDIT_WORKOUT_COMMENT](
    context: ActionContext<IWorkoutsState, IRootState>,
    payload: ICommentForm
  ): void
  [WORKOUTS_STORE.ACTIONS.LIKE_COMMENT](
    context: ActionContext<IWorkoutsState, IRootState>,
    comment: IComment
  ): void
  [WORKOUTS_STORE.ACTIONS.LIKE_WORKOUT](
    context: ActionContext<IWorkoutsState, IRootState>,
    workoutId: string
  ): void
  [WORKOUTS_STORE.ACTIONS.MAKE_APPEAL](
    context: ActionContext<IWorkoutsState, IRootState>,
    payload: IAppealPayload
  ): void
  [WORKOUTS_STORE.ACTIONS.UNDO_LIKE_COMMENT](
    context: ActionContext<IWorkoutsState, IRootState>,
    comment: IComment
  ): void
  [WORKOUTS_STORE.ACTIONS.UNDO_LIKE_WORKOUT](
    context: ActionContext<IWorkoutsState, IRootState>,
    workoutId: string
  ): void
  [WORKOUTS_STORE.ACTIONS.GET_LIKES](
    context: ActionContext<IWorkoutsState, IRootState>,
    payload: ILikesPayload
  ): void
  [WORKOUTS_STORE.ACTIONS.REFRESH_WORKOUT](
    context: ActionContext<IWorkoutsState, IRootState>,
    workoutId: string
  ): void
  [WORKOUTS_STORE.ACTIONS.GET_LOCATION_FROM_QUERY](
    context: ActionContext<IWorkoutsState, IRootState>,
    query: string
  ): void
  [WORKOUTS_STORE.ACTIONS.GET_WORKOUT_GEOJSON](
    context: ActionContext<IWorkoutsState, IRootState>,
    workoutId: string
  ): void
  [WORKOUTS_STORE.ACTIONS.UPDATE_ELEVATION_DATA_SOURCES](
    context: ActionContext<IWorkoutsState, IRootState>,
    payload: IWorkoutElevationSourceDataPayload
  ): void
}

export interface IWorkoutsGetters {
  [WORKOUTS_STORE.GETTERS.APPEAL_LOADING](state: IWorkoutsState): null | string
  [WORKOUTS_STORE.GETTERS.CALENDAR_WORKOUTS](state: IWorkoutsState): IWorkout[]
  [WORKOUTS_STORE.GETTERS.CURRENT_REPORTING](state: IWorkoutsState): boolean
  [WORKOUTS_STORE.GETTERS.SUCCESS](state: IWorkoutsState): null | string
  [WORKOUTS_STORE.GETTERS.TIMELINE_WORKOUTS](state: IWorkoutsState): IWorkout[]
  [WORKOUTS_STORE.GETTERS.AUTH_USER_WORKOUTS](state: IWorkoutsState): IWorkout[]
  [WORKOUTS_STORE.GETTERS.AUTH_USER_WORKOUTS_COLLECTION](
    state: IWorkoutsState
  ): IWorkoutsFeatureCollection
  [WORKOUTS_STORE.GETTERS.WORKOUT_CONTENT_EDITION](
    state: IWorkoutsState
  ): IWorkoutContentEdition
  [WORKOUTS_STORE.GETTERS.WORKOUT_DATA](state: IWorkoutsState): IWorkoutData
  [WORKOUTS_STORE.GETTERS.WORKOUT_GEOJSON](
    state: IWorkoutsState
  ): GeoJSON | null
  [WORKOUTS_STORE.GETTERS.WORKOUTS_PAGINATION](
    state: IWorkoutsState
  ): IPagination
  [WORKOUTS_STORE.GETTERS.WORKOUTS_STATISTICS](
    state: IWorkoutsState
  ): TWorkoutsStatistics
  [WORKOUTS_STORE.GETTERS.GEOCODE_LOADING](state: IWorkoutsState): boolean
  [WORKOUTS_STORE.GETTERS.MAP_LOADING](state: IWorkoutsState): boolean
}

export type TWorkoutsMutations<S = IWorkoutsState> = {
  [WORKOUTS_STORE.MUTATIONS.ADD_TIMELINE_WORKOUTS](
    state: S,
    workouts: IWorkout[]
  ): void
  [WORKOUTS_STORE.MUTATIONS.SET_APPEAL_LOADING](
    state: S,
    loading: null | string
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
  [WORKOUTS_STORE.MUTATIONS.SET_USER_WORKOUTS_COLLECTION](
    state: S,
    featureCollection: IWorkoutsFeatureCollection
  ): void
  [WORKOUTS_STORE.MUTATIONS.SET_WORKOUT](state: S, workout: IWorkout): void
  [WORKOUTS_STORE.MUTATIONS.SET_WORKOUT_CHART_DATA](
    state: S,
    chartDate: IWorkoutApiChartData[]
  ): void
  [WORKOUTS_STORE.MUTATIONS.SET_WORKOUT_CHART_DATA_LOADING](
    state: S,
    loading: boolean
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
  [WORKOUTS_STORE.MUTATIONS.SET_WORKOUT_GEOJSON](
    state: S,
    geojson: GeoJSON | null
  ): void
  [WORKOUTS_STORE.MUTATIONS.SET_WORKOUT_LOADING](
    state: S,
    loading: boolean
  ): void
  [WORKOUTS_STORE.MUTATIONS.SET_WORKOUTS_PAGINATION](
    state: S,
    pagination: IPagination
  ): void
  [WORKOUTS_STORE.MUTATIONS.SET_WORKOUTS_STATISTICS](
    state: S,
    totals: TWorkoutsStatistics
  ): void
  [WORKOUTS_STORE.MUTATIONS.EMPTY_CALENDAR_WORKOUTS](state: S): void
  [WORKOUTS_STORE.MUTATIONS.EMPTY_WORKOUTS](state: S): void
  [WORKOUTS_STORE.MUTATIONS.EMPTY_WORKOUT](state: S): void
  [WORKOUTS_STORE.MUTATIONS.SET_WORKOUT_COMMENTS](
    state: S,
    comments: IComment[]
  ): void
  [WORKOUTS_STORE.MUTATIONS.ADD_WORKOUT_COMMENT](
    state: S,
    comment: IComment
  ): void
  [WORKOUTS_STORE.MUTATIONS.SET_COMMENT_LOADING](
    state: S,
    commentId: string | null
  ): void
  [WORKOUTS_STORE.MUTATIONS.SET_CURRENT_COMMENT_EDITION](
    state: S,
    currentCommentEdition: ICurrentCommentEdition
  ): void
  [WORKOUTS_STORE.MUTATIONS.SET_CURRENT_REPORTING](
    state: S,
    currentReporting: boolean
  ): void
  [WORKOUTS_STORE.MUTATIONS.SET_SUCCESS](state: S, success: null | string): void
  [WORKOUTS_STORE.MUTATIONS.SET_REFRESH_LOADING](
    state: S,
    refreshLoading: boolean
  ): void
  [WORKOUTS_STORE.MUTATIONS.SET_GEOCODE_LOADING](
    state: S,
    geocodeLoading: boolean
  ): void
  [WORKOUTS_STORE.MUTATIONS.SET_MAP_LOADING](
    state: S,
    mapLoading: boolean
  ): void
  [WORKOUTS_STORE.MUTATIONS.SET_ELEVATION_DATA_LOADING](
    state: S,
    elevationLoading: boolean
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
    P extends Parameters<TWorkoutsMutations[K]>[1],
  >(
    key: K,
    payload?: P,
    options?: CommitOptions
  ): ReturnType<TWorkoutsMutations[K]>
}
