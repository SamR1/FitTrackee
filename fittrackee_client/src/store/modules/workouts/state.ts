import type { IWorkoutsState } from '@/store/modules/workouts/types'
import type { IPagination } from '@/types/api'
import type {
  ICurrentCommentEdition,
  IWorkout,
  TWorkoutsStatistics,
} from '@/types/workouts'

export const workoutsState: IWorkoutsState = {
  calendar_workouts: [],
  timeline_workouts: [],
  pagination: <IPagination>{},
  user_workouts: [],
  user_workouts_collection: {
    bbox: [],
    features: [],
    type: 'FeatureCollection',
  },
  user_workouts_statistics: <TWorkoutsStatistics>{},
  workoutData: {
    geojson: null,
    gpx: '',
    loading: false,
    workout: <IWorkout>{},
    chartData: [],
    chartDataLoading: false,
    comments: [],
    commentsLoading: null,
    currentCommentEdition: <ICurrentCommentEdition>{},
    currentReporting: false,
    refreshLoading: false,
  },
  workoutContent: {
    loading: false,
    contentType: '',
  },
  success: null,
  appealLoading: null,
  geocodeLoading: false,
  mapLoading: false,
  likes: [],
}
