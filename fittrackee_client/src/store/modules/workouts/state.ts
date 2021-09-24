import { IWorkoutsState } from '@/store/modules/workouts/types'
import { IWorkout } from '@/types/workouts'

export const workoutsState: IWorkoutsState = {
  calendar_workouts: [],
  user_workouts: [],
  workout: {
    gpx: '',
    loading: false,
    workout: <IWorkout>{},
  },
}
