import { IWorkoutsState } from '@/store/modules/workouts/types'
import { IWorkout } from '@/types/workouts'

export const initialWorkoutValue = {
  gpx: '',
  loading: false,
  workout: <IWorkout>{},
  chartData: [],
}

export const workoutsState: IWorkoutsState = {
  calendar_workouts: [],
  user_workouts: [],
  workoutData: initialWorkoutValue,
}
