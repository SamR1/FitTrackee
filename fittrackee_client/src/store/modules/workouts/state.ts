import type { IWorkoutsState } from '@/store/modules/workouts/types'
import type { IPagination } from '@/types/api'
import type { IWorkout } from '@/types/workouts'

export const workoutsState: IWorkoutsState = {
  calendar_workouts: [],
  timeline_workouts: [],
  pagination: <IPagination>{},
  user_workouts: [],
  workoutData: {
    gpx: '',
    loading: false,
    workout: <IWorkout>{},
    chartData: [],
  },
}
