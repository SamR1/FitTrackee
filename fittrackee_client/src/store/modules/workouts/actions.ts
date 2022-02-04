import { ActionContext, ActionTree } from 'vuex'

import authApi from '@/api/authApi'
import router from '@/router'
import { ROOT_STORE, AUTH_USER_STORE, WORKOUTS_STORE } from '@/store/constants'
import { IRootState } from '@/store/modules/root/types'
import { WorkoutsMutations } from '@/store/modules/workouts/enums'
import {
  IWorkoutsActions,
  IWorkoutsState,
} from '@/store/modules/workouts/types'
import {
  IWorkout,
  IWorkoutForm,
  IWorkoutPayload,
  TWorkoutsPayload,
} from '@/types/workouts'
import { handleError } from '@/utils'

const getWorkouts = (
  context: ActionContext<IWorkoutsState, IRootState>,
  payload: TWorkoutsPayload,
  target: WorkoutsMutations
): void => {
  context.commit(ROOT_STORE.MUTATIONS.EMPTY_ERROR_MESSAGES)
  authApi
    .get(target.match('TIMELINE') ? 'timeline' : 'workouts', {
      params: payload,
    })
    .then((res) => {
      if (res.data.status === 'success') {
        context.commit(WORKOUTS_STORE.MUTATIONS[target], res.data.data.workouts)
        if (target === WorkoutsMutations['SET_USER_WORKOUTS']) {
          context.commit(
            WORKOUTS_STORE.MUTATIONS.SET_WORKOUTS_PAGINATION,
            res.data.pagination
          )
        }
      } else {
        handleError(context, null)
      }
    })
    .catch((error) => handleError(context, error))
}

export const actions: ActionTree<IWorkoutsState, IRootState> &
  IWorkoutsActions = {
  [WORKOUTS_STORE.ACTIONS.GET_CALENDAR_WORKOUTS](
    context: ActionContext<IWorkoutsState, IRootState>,
    payload: TWorkoutsPayload
  ): void {
    context.commit(WORKOUTS_STORE.MUTATIONS.EMPTY_CALENDAR_WORKOUTS)
    getWorkouts(context, payload, WorkoutsMutations['SET_CALENDAR_WORKOUTS'])
  },
  [WORKOUTS_STORE.ACTIONS.GET_USER_WORKOUTS](
    context: ActionContext<IWorkoutsState, IRootState>,
    payload: TWorkoutsPayload
  ): void {
    getWorkouts(context, payload, WorkoutsMutations['SET_USER_WORKOUTS'])
  },
  [WORKOUTS_STORE.ACTIONS.GET_TIMELINE_WORKOUTS](
    context: ActionContext<IWorkoutsState, IRootState>,
    payload: TWorkoutsPayload
  ): void {
    getWorkouts(context, payload, WorkoutsMutations['SET_TIMELINE_WORKOUTS'])
  },
  [WORKOUTS_STORE.ACTIONS.GET_MORE_TIMELINE_WORKOUTS](
    context: ActionContext<IWorkoutsState, IRootState>,
    payload: TWorkoutsPayload
  ): void {
    getWorkouts(context, payload, WorkoutsMutations['ADD_TIMELINE_WORKOUTS'])
  },
  [WORKOUTS_STORE.ACTIONS.GET_WORKOUT_DATA](
    context: ActionContext<IWorkoutsState, IRootState>,
    payload: IWorkoutPayload
  ): void {
    context.commit(ROOT_STORE.MUTATIONS.EMPTY_ERROR_MESSAGES)
    context.commit(WORKOUTS_STORE.MUTATIONS.SET_WORKOUT_LOADING, true)
    const segmentUrl = payload.segmentId ? `/segment/${payload.segmentId}` : ''
    authApi
      .get(`workouts/${payload.workoutId}`)
      .then((res) => {
        const workout: IWorkout = res.data.data.workouts[0]
        if (res.data.status === 'success') {
          if (
            payload.segmentId &&
            (workout.segments.length === 0 ||
              !workout.segments[+payload.segmentId - 1])
          ) {
            throw new Error('WORKOUT_NOT_FOUND')
          }
          context.commit(
            WORKOUTS_STORE.MUTATIONS.SET_WORKOUT,
            res.data.data.workouts[0]
          )
          if (res.data.data.workouts[0].with_gpx) {
            authApi
              .get(`workouts/${payload.workoutId}/chart_data${segmentUrl}`)
              .then((res) => {
                if (res.data.status === 'success') {
                  context.commit(
                    WORKOUTS_STORE.MUTATIONS.SET_WORKOUT_CHART_DATA,
                    res.data.data.chart_data
                  )
                }
              })
            authApi
              .get(`workouts/${payload.workoutId}/gpx${segmentUrl}`)
              .then((res) => {
                if (res.data.status === 'success') {
                  context.commit(
                    WORKOUTS_STORE.MUTATIONS.SET_WORKOUT_GPX,
                    res.data.data.gpx
                  )
                }
              })
          }
        } else {
          context.commit(WORKOUTS_STORE.MUTATIONS.EMPTY_WORKOUT)
          handleError(context, null)
        }
      })
      .catch((error) => {
        context.commit(WORKOUTS_STORE.MUTATIONS.EMPTY_WORKOUT)
        handleError(context, error)
      })
      .finally(() =>
        context.commit(WORKOUTS_STORE.MUTATIONS.SET_WORKOUT_LOADING, false)
      )
  },
  [WORKOUTS_STORE.ACTIONS.DELETE_WORKOUT](
    context: ActionContext<IWorkoutsState, IRootState>,
    payload: IWorkoutPayload
  ): void {
    context.commit(ROOT_STORE.MUTATIONS.EMPTY_ERROR_MESSAGES)
    context.commit(WORKOUTS_STORE.MUTATIONS.SET_WORKOUT_LOADING, true)
    authApi
      .delete(`workouts/${payload.workoutId}`)
      .then(() => {
        context.commit(WORKOUTS_STORE.MUTATIONS.EMPTY_WORKOUT)
        context.dispatch(AUTH_USER_STORE.ACTIONS.GET_USER_PROFILE)
        router.push('/')
      })
      .catch((error) => {
        handleError(context, error)
      })
      .finally(() =>
        context.commit(WORKOUTS_STORE.MUTATIONS.SET_WORKOUT_LOADING, false)
      )
  },
  [WORKOUTS_STORE.ACTIONS.EDIT_WORKOUT](
    context: ActionContext<IWorkoutsState, IRootState>,
    payload: IWorkoutPayload
  ): void {
    context.commit(ROOT_STORE.MUTATIONS.EMPTY_ERROR_MESSAGES)
    context.commit(WORKOUTS_STORE.MUTATIONS.SET_WORKOUT_LOADING, true)
    authApi
      .patch(`workouts/${payload.workoutId}`, payload.data)
      .then(() => {
        context.dispatch(AUTH_USER_STORE.ACTIONS.GET_USER_PROFILE)
        context
          .dispatch(WORKOUTS_STORE.ACTIONS.GET_WORKOUT_DATA, {
            workoutId: payload.workoutId,
          })
          .then(() => {
            router.push({
              name: 'Workout',
              params: { workoutId: payload.workoutId },
            })
          })
      })
      .catch((error) => {
        handleError(context, error)
      })
      .finally(() =>
        context.commit(WORKOUTS_STORE.MUTATIONS.SET_WORKOUT_LOADING, false)
      )
  },
  [WORKOUTS_STORE.ACTIONS.ADD_WORKOUT](
    context: ActionContext<IWorkoutsState, IRootState>,
    payload: IWorkoutForm
  ): void {
    context.commit(ROOT_STORE.MUTATIONS.EMPTY_ERROR_MESSAGES)
    context.commit(WORKOUTS_STORE.MUTATIONS.SET_WORKOUT_LOADING, true)
    if (!payload.file) {
      throw new Error('No file part')
    }
    const form = new FormData()
    form.append('file', payload.file)
    form.append(
      'data',
      `{"sport_id": ${payload.sport_id}, "notes": "${payload.notes}",` +
        ` "workout_visibility": "${payload.workout_visibility}",` +
        ` "map_visibility": "${payload.map_visibility}"}`
    )
    authApi
      .post('workouts', form, {
        headers: {
          'content-type': 'multipart/form-data',
        },
      })
      .then((res) => {
        if (res.data.status === 'created') {
          context.dispatch(AUTH_USER_STORE.ACTIONS.GET_USER_PROFILE)
          const workout: IWorkout = res.data.data.workouts[0]
          router.push(
            res.data.data.workouts.length === 1
              ? `/workouts/${workout.id}`
              : '/'
          )
        }
      })
      .catch((error) => {
        handleError(context, error)
      })
      .finally(() =>
        context.commit(WORKOUTS_STORE.MUTATIONS.SET_WORKOUT_LOADING, false)
      )
  },
  [WORKOUTS_STORE.ACTIONS.ADD_WORKOUT_WITHOUT_GPX](
    context: ActionContext<IWorkoutsState, IRootState>,
    payload: IWorkoutForm
  ): void {
    context.commit(ROOT_STORE.MUTATIONS.EMPTY_ERROR_MESSAGES)
    context.commit(WORKOUTS_STORE.MUTATIONS.SET_WORKOUT_LOADING, true)
    authApi
      .post('workouts/no_gpx', payload)
      .then((res) => {
        if (res.data.status === 'created') {
          context.dispatch(AUTH_USER_STORE.ACTIONS.GET_USER_PROFILE)
          const workout: IWorkout = res.data.data.workouts[0]
          router.push(`/workouts/${workout.id}`)
        }
      })
      .catch((error) => {
        handleError(context, error)
      })
      .finally(() =>
        context.commit(WORKOUTS_STORE.MUTATIONS.SET_WORKOUT_LOADING, false)
      )
  },
}
