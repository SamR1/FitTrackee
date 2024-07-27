import type { MutationTree } from 'vuex'

import { WORKOUTS_STORE } from '@/store/constants'
import type {
  IWorkoutsState,
  TWorkoutsMutations,
} from '@/store/modules/workouts/types'
import type { IPagination } from '@/types/api'
import type {
  IComment,
  ICurrentCommentEdition,
  IWorkout,
  IWorkoutApiChartData,
} from '@/types/workouts'

export const mutations: MutationTree<IWorkoutsState> & TWorkoutsMutations = {
  [WORKOUTS_STORE.MUTATIONS.ADD_TIMELINE_WORKOUTS](
    state: IWorkoutsState,
    workouts: IWorkout[]
  ) {
    state.timeline_workouts = state.timeline_workouts.concat(workouts)
  },
  [WORKOUTS_STORE.MUTATIONS.SET_APPEAL_LOADING](
    state: IWorkoutsState,
    loading: null | string
  ) {
    state.appealLoading = loading
  },
  [WORKOUTS_STORE.MUTATIONS.SET_CALENDAR_WORKOUTS](
    state: IWorkoutsState,
    workouts: IWorkout[]
  ) {
    state.calendar_workouts = workouts
  },
  [WORKOUTS_STORE.MUTATIONS.SET_SUCCESS](
    state: IWorkoutsState,
    success: null | string
  ) {
    state.success = success
  },
  [WORKOUTS_STORE.MUTATIONS.SET_TIMELINE_WORKOUTS](
    state: IWorkoutsState,
    workouts: IWorkout[]
  ) {
    state.timeline_workouts = workouts
  },
  [WORKOUTS_STORE.MUTATIONS.SET_USER_WORKOUTS](
    state: IWorkoutsState,
    workouts: IWorkout[]
  ) {
    state.user_workouts = workouts
  },
  [WORKOUTS_STORE.MUTATIONS.SET_WORKOUTS_PAGINATION](
    state: IWorkoutsState,
    pagination: IPagination
  ) {
    state.pagination = pagination
  },
  [WORKOUTS_STORE.MUTATIONS.SET_WORKOUT](
    state: IWorkoutsState,
    workout: IWorkout
  ) {
    state.workoutData.workout = workout
  },
  [WORKOUTS_STORE.MUTATIONS.SET_WORKOUT_CHART_DATA](
    state: IWorkoutsState,
    chartData: IWorkoutApiChartData[]
  ) {
    state.workoutData.chartData = chartData
  },
  [WORKOUTS_STORE.MUTATIONS.SET_WORKOUT_GPX](
    state: IWorkoutsState,
    gpx: string
  ) {
    state.workoutData.gpx = gpx
  },
  [WORKOUTS_STORE.MUTATIONS.SET_WORKOUT_LOADING](
    state: IWorkoutsState,
    loading: boolean
  ) {
    state.workoutData.loading = loading
  },
  [WORKOUTS_STORE.MUTATIONS.EMPTY_CALENDAR_WORKOUTS](state: IWorkoutsState) {
    state.calendar_workouts = []
  },
  [WORKOUTS_STORE.MUTATIONS.EMPTY_WORKOUTS](state: IWorkoutsState) {
    state.calendar_workouts = []
    state.user_workouts = []
    state.timeline_workouts = []
  },
  [WORKOUTS_STORE.MUTATIONS.EMPTY_WORKOUT](state: IWorkoutsState) {
    state.workoutData = {
      gpx: '',
      loading: false,
      workout: <IWorkout>{},
      chartData: [],
      comments: [],
      commentsLoading: null,
      currentCommentEdition: <ICurrentCommentEdition>{},
      currentReporting: false,
    }
  },
  [WORKOUTS_STORE.MUTATIONS.SET_WORKOUT_COMMENTS](
    state: IWorkoutsState,
    comments: IComment[]
  ) {
    state.workoutData.comments = comments
  },
  [WORKOUTS_STORE.MUTATIONS.ADD_WORKOUT_COMMENT](
    state: IWorkoutsState,
    comment: IComment
  ) {
    state.workoutData.comments.push(comment)
  },
  [WORKOUTS_STORE.MUTATIONS.SET_COMMENT_LOADING](
    state: IWorkoutsState,
    commentId: string | null
  ) {
    state.workoutData.commentsLoading = commentId
  },
  [WORKOUTS_STORE.MUTATIONS.SET_CURRENT_COMMENT_EDITION](
    state: IWorkoutsState,
    currentCommentEdition: ICurrentCommentEdition
  ) {
    state.workoutData.currentCommentEdition = currentCommentEdition
  },
  [WORKOUTS_STORE.MUTATIONS.SET_CURRENT_REPORTING](
    state: IWorkoutsState,
    currentReporting: boolean
  ) {
    state.workoutData.currentReporting = currentReporting
  },
}
