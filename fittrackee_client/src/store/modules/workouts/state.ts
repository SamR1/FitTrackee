import { IWorkoutsState } from '@/store/modules/workouts/types'
import { IWorkout } from '@/types/workouts'

export const workoutsState: IWorkoutsState = {
  calendar_workouts: [],
  timeline_workouts: [],
  user_workouts: [],
  workoutData: {
    gpx: '',
    loading: false,
    workout: <IWorkout>{},
    chartData: [],
  },
}
