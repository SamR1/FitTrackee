import type { ActionContext, ActionTree } from 'vuex'

import authApi from '@/api/authApi'
import router from '@/router'
import {
  AUTH_USER_STORE,
  ROOT_STORE,
  WORKOUTS_STORE,
  USERS_STORE,
} from '@/store/constants'
import type { IRootState } from '@/store/modules/root/types'
import { WorkoutsMutations } from '@/store/modules/workouts/enums'
import type {
  IWorkoutsActions,
  IWorkoutsState,
} from '@/store/modules/workouts/types'
import type {
  ICommentForm,
  IWorkout,
  IWorkoutContentPayload,
  IWorkoutForm,
  IWorkoutPayload,
  TWorkoutsPayload,
  ICommentPayload,
  IComment,
  IAppealPayload,
  ILikesPayload,
  TWorkoutsMapPayload,
  IWorkoutElevationSourceDataPayload,
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
      params: {
        ...payload,
        ...(target === 'SET_USER_WORKOUTS' ? { with_statistics: true } : {}),
      },
    })
    .then((res) => {
      if (res.data.status === 'success') {
        context.commit(WORKOUTS_STORE.MUTATIONS[target], res.data.data.workouts)
        if (
          [
            WorkoutsMutations['SET_USER_WORKOUTS'],
            WorkoutsMutations['SET_TIMELINE_WORKOUTS'],
            WorkoutsMutations['ADD_TIMELINE_WORKOUTS'],
          ].includes(target)
        ) {
          context.commit(
            WORKOUTS_STORE.MUTATIONS.SET_WORKOUTS_PAGINATION,
            res.data.pagination
          )
        }
        if (target === WorkoutsMutations['SET_USER_WORKOUTS']) {
          context.commit(
            WORKOUTS_STORE.MUTATIONS.SET_WORKOUTS_STATISTICS,
            res.data.data.statistics
          )
        }
      } else {
        handleError(context, null)
      }
    })
    .catch((error) => handleError(context, error))
}

const reloadComment = (
  context: ActionContext<IWorkoutsState, IRootState>,
  commentId: string | undefined,
  workoutId: string | undefined
) => {
  if (workoutId) {
    context.dispatch(WORKOUTS_STORE.ACTIONS.GET_WORKOUT_COMMENTS, workoutId)
  } else {
    context.dispatch(WORKOUTS_STORE.ACTIONS.GET_WORKOUT_COMMENT, commentId)
  }
}

const handleCommentLike = (
  context: ActionContext<IWorkoutsState, IRootState>,
  comment: IComment,
  undo = false
) => {
  authApi
    .post(`comments/${comment.id}/like${undo ? '/undo' : ''}`)
    .then((res) => {
      if (res.data.status === 'success') {
        reloadComment(context, comment.id, comment.workout_id)
      }
    })
    .catch((error) => {
      handleError(context, error)
    })
}

const handleWorkoutLike = (
  context: ActionContext<IWorkoutsState, IRootState>,
  workoutId: string,
  undo = false
) => {
  authApi
    .post(`workouts/${workoutId}/like${undo ? '/undo' : ''}`)
    .then((res) => {
      if (res.data.status === 'success') {
        context.commit(
          WORKOUTS_STORE.MUTATIONS.SET_WORKOUT,
          res.data.data.workouts[0]
        )
      }
    })
    .catch((error) => {
      handleError(context, error)
    })
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
  [WORKOUTS_STORE.ACTIONS.GET_AUTH_USER_WORKOUTS](
    context: ActionContext<IWorkoutsState, IRootState>,
    payload: TWorkoutsPayload
  ): void {
    getWorkouts(context, payload, WorkoutsMutations['SET_USER_WORKOUTS'])
  },
  [WORKOUTS_STORE.ACTIONS.GET_AUTH_USER_WORKOUTS_COLLECTION](
    context: ActionContext<IWorkoutsState, IRootState>,
    payload: TWorkoutsPayload
  ): void {
    context.commit(ROOT_STORE.MUTATIONS.EMPTY_ERROR_MESSAGES)
    context.commit(WORKOUTS_STORE.MUTATIONS.SET_MAP_LOADING, true)
    authApi
      .get('workouts/collection', {
        params: payload,
      })
      .then((res) => {
        if (res.data.status === 'success') {
          context.commit(
            WORKOUTS_STORE.MUTATIONS.SET_USER_WORKOUTS_COLLECTION,
            res.data.data
          )
          context.commit(
            WORKOUTS_STORE.MUTATIONS.SET_WORKOUTS_PAGINATION,
            res.data.pagination
          )
        } else {
          handleError(context, null)
        }
      })
      .catch((error) => handleError(context, error))
      .finally(() =>
        context.commit(WORKOUTS_STORE.MUTATIONS.SET_MAP_LOADING, false)
      )
  },
  [WORKOUTS_STORE.ACTIONS.GET_AUTH_USER_WORKOUTS_FOR_GLOBAl_MAP](
    context: ActionContext<IWorkoutsState, IRootState>,
    payload: TWorkoutsMapPayload
  ): void {
    context.commit(ROOT_STORE.MUTATIONS.EMPTY_ERROR_MESSAGES)
    context.commit(WORKOUTS_STORE.MUTATIONS.SET_MAP_LOADING, true)
    authApi
      .get(`workouts/global-map`, {
        params: payload,
      })
      .then((res) => {
        if (res.data.status === 'success') {
          context.commit(
            WORKOUTS_STORE.MUTATIONS.SET_USER_WORKOUTS_COLLECTION,
            res.data.data
          )
        } else {
          handleError(context, null)
        }
      })
      .catch((error) => handleError(context, error))
      .finally(() =>
        context.commit(WORKOUTS_STORE.MUTATIONS.SET_MAP_LOADING, false)
      )
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
              !workout.segments.find(
                (segment) => segment.segment_id === payload.segmentId
              ))
          ) {
            throw new Error('WORKOUT_NOT_FOUND')
          }
          context.commit(WORKOUTS_STORE.MUTATIONS.SET_WORKOUT, workout)
          if (workout.with_analysis) {
            context.commit(
              WORKOUTS_STORE.MUTATIONS.SET_WORKOUT_CHART_DATA_LOADING,
              true
            )
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
              .catch(() => {
                context.commit(
                  WORKOUTS_STORE.MUTATIONS.SET_WORKOUT_CHART_DATA,
                  []
                )
              })
              .finally(() => {
                context.commit(
                  WORKOUTS_STORE.MUTATIONS.SET_WORKOUT_CHART_DATA_LOADING,
                  false
                )
              })
          }
          if (workout.with_geometry) {
            authApi
              .get(`workouts/${payload.workoutId}/geojson${segmentUrl}`)
              .then((res) => {
                if (res.data.status === 'success') {
                  context.commit(
                    WORKOUTS_STORE.MUTATIONS.SET_WORKOUT_GEOJSON,
                    res.data.data.geojson
                  )
                }
              })
          }
          if (!payload.segmentId) {
            context.dispatch(
              WORKOUTS_STORE.ACTIONS.GET_WORKOUT_COMMENTS,
              workout.id
            )
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
        context.dispatch(AUTH_USER_STORE.ACTIONS.GET_USER_PROFILE, {})
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
        context.dispatch(AUTH_USER_STORE.ACTIONS.GET_USER_PROFILE, {})
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
  [WORKOUTS_STORE.ACTIONS.EDIT_WORKOUT_CONTENT](
    context: ActionContext<IWorkoutsState, IRootState>,
    payload: IWorkoutContentPayload
  ): void {
    context.commit(WORKOUTS_STORE.MUTATIONS.SET_WORKOUT_CONTENT_LOADING, true)
    context.commit(
      WORKOUTS_STORE.MUTATIONS.SET_WORKOUT_CONTENT_TYPE,
      payload.contentType
    )
    context.commit(ROOT_STORE.MUTATIONS.EMPTY_ERROR_MESSAGES)
    const data = {
      [payload.contentType === 'NOTES' ? 'notes' : 'description']:
        payload.content,
    }
    authApi
      .patch(`workouts/${payload.workoutId}`, data)
      .then((res) => {
        const workout: IWorkout = res.data.data.workouts[0]
        context.commit(WORKOUTS_STORE.MUTATIONS.SET_WORKOUT_CONTENT, workout)
      })
      .catch((error) => {
        handleError(context, error)
      })
      .finally(() =>
        context.commit(
          WORKOUTS_STORE.MUTATIONS.SET_WORKOUT_CONTENT_LOADING,
          false
        )
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
    const notes = payload.notes.replace(/"/g, '\\"')
    const description = payload.description.replace(/"/g, '\\"')
    const title = payload.title.replace(/"/g, '\\"')
    const form = new FormData()
    form.append('file', payload.file)
    form.append(
      'data',
      `{"sport_id": ${payload.sport_id}, "notes": "${notes}",` +
        ` "description": "${description}", "title": "${title}", ` +
        ` "equipment_ids": [${payload.equipment_ids.map((e) => `"${e}"`).join(',')}],` +
        ` "workout_visibility": "${payload.workout_visibility}",` +
        ` "analysis_visibility": "${payload.analysis_visibility}",` +
        ` "map_visibility": "${payload.map_visibility}"}`
    )
    authApi
      .post('workouts', form, {
        headers: {
          'content-type': 'multipart/form-data',
        },
      })
      .then((res) => {
        if (res.data.status === 'in_progress') {
          router.push(`/profile/archive-uploads/${res.data.data.task_id}`)
        } else if (res.data.status === 'created') {
          context.dispatch(AUTH_USER_STORE.ACTIONS.GET_USER_PROFILE, {})
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
          context.dispatch(AUTH_USER_STORE.ACTIONS.GET_USER_PROFILE, {})
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
  [WORKOUTS_STORE.ACTIONS.ADD_COMMENT](
    context: ActionContext<IWorkoutsState, IRootState>,
    payload: ICommentForm
  ): void {
    context.commit(WORKOUTS_STORE.MUTATIONS.SET_COMMENT_LOADING, 'new')
    const data = {
      text: payload.text,
      text_visibility: payload.text_visibility,
    }
    context.commit(ROOT_STORE.MUTATIONS.EMPTY_ERROR_MESSAGES)
    authApi
      .post(`/workouts/${payload.workout_id}/comments`, data)
      .then((res) => {
        if (res.data.status === 'created') {
          context.dispatch(
            WORKOUTS_STORE.ACTIONS.GET_WORKOUT_COMMENTS,
            payload.workout_id
          )
          context.commit(
            WORKOUTS_STORE.MUTATIONS.SET_CURRENT_COMMENT_EDITION,
            {}
          )
        } else {
          handleError(context, null)
        }
      })
      .catch((error) => {
        handleError(context, error)
        context.commit(WORKOUTS_STORE.MUTATIONS.SET_COMMENT_LOADING, null)
      })
  },
  [WORKOUTS_STORE.ACTIONS.GET_WORKOUT_COMMENT](
    context: ActionContext<IWorkoutsState, IRootState>,
    commentId: string
  ): void {
    context.commit(WORKOUTS_STORE.MUTATIONS.SET_COMMENT_LOADING, 'loading')
    context.commit(ROOT_STORE.MUTATIONS.EMPTY_ERROR_MESSAGES)
    authApi
      .get(`/comments/${commentId}`)
      .then((res) => {
        if (res.data.status === 'success') {
          context.commit(WORKOUTS_STORE.MUTATIONS.SET_WORKOUT_COMMENTS, [
            res.data.comment,
          ])
          context.commit(WORKOUTS_STORE.MUTATIONS.SET_COMMENT_LOADING, null)
        } else {
          handleError(context, null)
        }
      })
      .catch((error) => {
        handleError(context, error)
      })
      .finally(() =>
        context.commit(WORKOUTS_STORE.MUTATIONS.SET_COMMENT_LOADING, null)
      )
  },
  [WORKOUTS_STORE.ACTIONS.GET_WORKOUT_COMMENTS](
    context: ActionContext<IWorkoutsState, IRootState>,
    workoutId: string
  ): void {
    context.commit(ROOT_STORE.MUTATIONS.EMPTY_ERROR_MESSAGES)
    authApi
      .get(`/workouts/${workoutId}/comments`)
      .then((res) => {
        if (res.data.status === 'success') {
          context.commit(
            WORKOUTS_STORE.MUTATIONS.SET_WORKOUT_COMMENTS,
            res.data.data.comments
          )
          context.commit(WORKOUTS_STORE.MUTATIONS.SET_COMMENT_LOADING, null)
        } else {
          handleError(context, null)
        }
      })
      .catch((error) => {
        handleError(
          context,
          error.status === 500 ? null : error,
          'error when getting comments'
        )
      })
      .finally(() =>
        context.commit(WORKOUTS_STORE.MUTATIONS.SET_COMMENT_LOADING, null)
      )
  },
  [WORKOUTS_STORE.ACTIONS.DELETE_WORKOUT_COMMENT](
    context: ActionContext<IWorkoutsState, IRootState>,
    payload: ICommentPayload
  ): void {
    context.commit(ROOT_STORE.MUTATIONS.EMPTY_ERROR_MESSAGES)
    context.commit(WORKOUTS_STORE.MUTATIONS.SET_COMMENT_LOADING, 'delete')
    authApi
      .delete(`comments/${payload.commentId}`)
      .then((res) => {
        if (res.status === 204) {
          if (payload.workoutId) {
            context.dispatch(
              WORKOUTS_STORE.ACTIONS.GET_WORKOUT_COMMENTS,
              payload.workoutId
            )
          } else {
            router.push('/')
          }
        }
      })
      .catch((error) => {
        handleError(context, error)
      })
  },
  [WORKOUTS_STORE.ACTIONS.EDIT_WORKOUT_COMMENT](
    context: ActionContext<IWorkoutsState, IRootState>,
    payload: ICommentForm
  ): void {
    context.commit(ROOT_STORE.MUTATIONS.EMPTY_ERROR_MESSAGES)
    context.commit(WORKOUTS_STORE.MUTATIONS.SET_COMMENT_LOADING, payload.id)
    authApi
      .patch(`comments/${payload.id}`, {
        text: payload.text,
      })
      .then((res) => {
        if (res.data.status === 'success') {
          reloadComment(context, payload.id, payload.workout_id)
          context.commit(
            WORKOUTS_STORE.MUTATIONS.SET_CURRENT_COMMENT_EDITION,
            {}
          )
        }
      })
      .catch((error) => {
        handleError(context, error)
        context.commit(WORKOUTS_STORE.MUTATIONS.SET_COMMENT_LOADING, null)
      })
  },
  [WORKOUTS_STORE.ACTIONS.LIKE_COMMENT](
    context: ActionContext<IWorkoutsState, IRootState>,
    comment: IComment
  ): void {
    handleCommentLike(context, comment)
  },
  [WORKOUTS_STORE.ACTIONS.UNDO_LIKE_COMMENT](
    context: ActionContext<IWorkoutsState, IRootState>,
    comment: IComment
  ): void {
    handleCommentLike(context, comment, true)
  },
  [WORKOUTS_STORE.ACTIONS.LIKE_WORKOUT](
    context: ActionContext<IWorkoutsState, IRootState>,
    workoutId: string
  ): void {
    handleWorkoutLike(context, workoutId)
  },
  [WORKOUTS_STORE.ACTIONS.UNDO_LIKE_WORKOUT](
    context: ActionContext<IWorkoutsState, IRootState>,
    workoutId: string
  ): void {
    handleWorkoutLike(context, workoutId, true)
  },
  [WORKOUTS_STORE.ACTIONS.MAKE_APPEAL](
    context: ActionContext<IWorkoutsState, IRootState>,
    payload: IAppealPayload
  ): void {
    const objectId = `${payload.objectType}_${payload.objectId}`
    context.commit(ROOT_STORE.MUTATIONS.EMPTY_ERROR_MESSAGES)
    context.commit(WORKOUTS_STORE.MUTATIONS.SET_APPEAL_LOADING, objectId)
    context.commit(WORKOUTS_STORE.MUTATIONS.SET_SUCCESS, null)
    authApi
      .post(`${payload.objectType}s/${payload.objectId}/suspension/appeal`, {
        text: payload.text,
      })
      .then((res) => {
        if (res.data.status === 'success') {
          context.commit(WORKOUTS_STORE.MUTATIONS.SET_SUCCESS, objectId)
        }
      })
      .catch((error) => {
        handleError(context, error)
      })
      .finally(() =>
        context.commit(WORKOUTS_STORE.MUTATIONS.SET_APPEAL_LOADING, null)
      )
  },
  [WORKOUTS_STORE.ACTIONS.GET_LIKES](
    context: ActionContext<IWorkoutsState, IRootState>,
    payload: ILikesPayload
  ): void {
    context.commit(ROOT_STORE.MUTATIONS.EMPTY_ERROR_MESSAGES)
    authApi
      .get(
        `${payload.objectType}s/${payload.objectId}/likes?page=${payload.page}`
      )
      .then((res) => {
        if (res.data.status === 'success') {
          context.commit(
            USERS_STORE.MUTATIONS.UPDATE_USERS,
            res.data.data.likes
          )
          context.commit(
            USERS_STORE.MUTATIONS.UPDATE_USERS_PAGINATION,
            res.data.pagination
          )
        }
      })
      .catch((error) => {
        handleError(context, error)
      })
  },
  [WORKOUTS_STORE.ACTIONS.REFRESH_WORKOUT](
    context: ActionContext<IWorkoutsState, IRootState>,
    workoutId: string
  ): void {
    context.commit(ROOT_STORE.MUTATIONS.EMPTY_ERROR_MESSAGES)
    context.commit(WORKOUTS_STORE.MUTATIONS.SET_REFRESH_LOADING, true)
    authApi
      .post(`workouts/${workoutId}/refresh`)
      .then((res) => {
        const workout: IWorkout = res.data.data.workouts[0]
        if (res.data.status === 'success') {
          context.commit(WORKOUTS_STORE.MUTATIONS.SET_WORKOUT, workout)
          if (workout.with_analysis) {
            context.commit(
              WORKOUTS_STORE.MUTATIONS.SET_WORKOUT_CHART_DATA_LOADING,
              true
            )
            authApi
              .get(`workouts/${workoutId}/chart_data`)
              .then((res) => {
                if (res.data.status === 'success') {
                  context.commit(
                    WORKOUTS_STORE.MUTATIONS.SET_WORKOUT_CHART_DATA,
                    res.data.data.chart_data
                  )
                }
              })
              .catch(() => {
                context.commit(
                  WORKOUTS_STORE.MUTATIONS.SET_WORKOUT_CHART_DATA,
                  []
                )
              })
              .finally(() => {
                context.commit(
                  WORKOUTS_STORE.MUTATIONS.SET_WORKOUT_CHART_DATA_LOADING,
                  false
                )
              })
          }
          if (workout.with_geometry) {
            authApi.get(`workouts/${workoutId}/geojson`).then((res) => {
              if (res.data.status === 'success') {
                context.commit(
                  WORKOUTS_STORE.MUTATIONS.SET_WORKOUT_GEOJSON,
                  res.data.data.geojson
                )
              }
            })
          }
          context.dispatch(
            WORKOUTS_STORE.ACTIONS.GET_WORKOUT_COMMENTS,
            workout.id
          )
        } else {
          context.commit(WORKOUTS_STORE.MUTATIONS.EMPTY_WORKOUT)
          handleError(context, null)
        }
      })
      .catch((error) => {
        context.dispatch(WORKOUTS_STORE.ACTIONS.GET_WORKOUT_DATA, { workoutId })
        handleError(context, error)
      })
      .finally(() =>
        context.commit(WORKOUTS_STORE.MUTATIONS.SET_REFRESH_LOADING, false)
      )
  },
  [WORKOUTS_STORE.ACTIONS.GET_LOCATION_FROM_QUERY](
    context: ActionContext<IWorkoutsState, IRootState>,
    query: string
  ): void {
    context.commit(ROOT_STORE.MUTATIONS.EMPTY_ERROR_MESSAGES)
    authApi
      .get('/geocode/search', { params: { query } })
      .then((res) => {
        if (res.data.status === 'success') {
          return res.data.locations
        }
        return []
      })
      .catch((error) => {
        handleError(context, error)
      })
  },
  [WORKOUTS_STORE.ACTIONS.GET_WORKOUT_GEOJSON](
    context: ActionContext<IWorkoutsState, IRootState>,
    workoutId: string
  ): void {
    context.commit(ROOT_STORE.MUTATIONS.EMPTY_ERROR_MESSAGES)
    authApi
      .get(`workouts/${workoutId}/geojson`)
      .then((res) => {
        if (res.data.status === 'success') {
          context.commit(
            WORKOUTS_STORE.MUTATIONS.SET_WORKOUT_GEOJSON,
            res.data.data.geojson
          )
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

  [WORKOUTS_STORE.ACTIONS.UPDATE_ELEVATION_DATA_SOURCES](
    context: ActionContext<IWorkoutsState, IRootState>,
    payload: IWorkoutElevationSourceDataPayload
  ): void {
    context.commit(ROOT_STORE.MUTATIONS.EMPTY_ERROR_MESSAGES)
    context.commit(WORKOUTS_STORE.MUTATIONS.SET_ELEVATION_DATA_LOADING, true)
    authApi
      .patch(`workouts/${payload.workoutId}`, {
        elevation_data_source: payload.elevationDataSource,
      })
      .then(() => {
        context.dispatch(AUTH_USER_STORE.ACTIONS.GET_USER_PROFILE, {})
        context.dispatch(WORKOUTS_STORE.ACTIONS.GET_WORKOUT_DATA, {
          workoutId: payload.workoutId,
        })
      })
      .catch(() => {
        handleError(context, null, 'Error when updating elevation data source')
      })
      .finally(() =>
        context.commit(
          WORKOUTS_STORE.MUTATIONS.SET_ELEVATION_DATA_LOADING,
          false
        )
      )
  },
}
