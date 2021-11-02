import { MutationTree } from 'vuex'

import { WORKOUTS_STORE } from '@/store/constants'
import {
  IWorkoutsState,
  TWorkoutsMutations,
} from '@/store/modules/workouts/types'
import { IWorkout, IWorkoutApiChartData } from '@/types/workouts'

export const mutations: MutationTree<IWorkoutsState> & TWorkoutsMutations = {
  [WORKOUTS_STORE.MUTATIONS.ADD_TIMELINE_WORKOUTS](
    state: IWorkoutsState,
    workouts: IWorkout[]
  ) {
    state.timeline_workouts = state.timeline_workouts.concat(workouts)
  },
  [WORKOUTS_STORE.MUTATIONS.SET_CALENDAR_WORKOUTS](
    state: IWorkoutsState,
    workouts: IWorkout[]
  ) {
    state.calendar_workouts = workouts
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
  },
  [WORKOUTS_STORE.MUTATIONS.EMPTY_WORKOUT](state: IWorkoutsState) {
    state.workoutData = {
      gpx: '',
      loading: false,
      workout: <IWorkout>{},
      chartData: [],
    }
  },
}
