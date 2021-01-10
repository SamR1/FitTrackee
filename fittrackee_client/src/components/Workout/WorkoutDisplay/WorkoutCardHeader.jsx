import React from 'react'
import { Link } from 'react-router-dom'

import { getDateWithTZ } from '../../../utils'
import { formatWorkoutDate } from '../../../utils/workouts'

export default function WorkoutCardHeader(props) {
  const {
    dataType,
    displayModal,
    segmentId,
    sport,
    t,
    title,
    user,
    workout,
  } = props
  const workoutDate = workout
    ? formatWorkoutDate(getDateWithTZ(workout.workout_date, user.timezone))
    : null

  const previousUrl =
    dataType === 'segment' && segmentId !== 1
      ? `/workouts/${workout.id}/segment/${segmentId - 1}`
      : dataType === 'workout' && workout.previous_workout
      ? `/workouts/${workout.previous_workout}`
      : null
  const nextUrl =
    dataType === 'segment' && segmentId < workout.segments.length
      ? `/workouts/${workout.id}/segment/${segmentId + 1}`
      : dataType === 'workout' && workout.next_workout
      ? `/workouts/${workout.next_workout}`
      : null

  return (
    <div className="container">
      <div className="row">
        <div className="col-auto">
          {previousUrl ? (
            <Link className="unlink" to={previousUrl}>
              <i
                className="fa fa-chevron-left"
                aria-hidden="true"
                title={t(`workouts:See previous ${dataType}`)}
              />
            </Link>
          ) : (
            <i
              className="fa fa-chevron-left inactive-link"
              aria-hidden="true"
              title={t(`workouts:No previous ${dataType}`)}
            />
          )}
        </div>
        <div className="col-auto col-workout-logo">
          <img className="sport-img-medium" src={sport.img} alt="sport logo" />
        </div>
        <div className="col">
          {dataType === 'workout' ? (
            <>
              {title}{' '}
              <Link className="unlink" to={`/workouts/${workout.id}/edit`}>
                <i
                  className="fa fa-edit custom-fa"
                  aria-hidden="true"
                  title={t('workouts:Edit workout')}
                />
              </Link>
              <i
                className="fa fa-trash custom-fa"
                aria-hidden="true"
                onClick={() => displayModal(true)}
                title={t('workouts:Delete workout')}
              />
            </>
          ) : (
            <>
              {/* prettier-ignore */}
              <Link
                to={`/workouts/${workout.id}`}
              >
                {title}
              </Link>{' '}
              - {t('workouts:segment')} {segmentId}
            </>
          )}
          <br />
          {workoutDate && (
            <span className="workout-date">
              {`${workoutDate.workout_date} - ${workoutDate.workout_time}`}
            </span>
          )}
        </div>
        <div className="col-auto">
          {nextUrl ? (
            <Link className="unlink" to={nextUrl}>
              <i
                className="fa fa-chevron-right"
                aria-hidden="true"
                title={t(`workouts:See next ${dataType}`)}
              />
            </Link>
          ) : (
            <i
              className="fa fa-chevron-right inactive-link"
              aria-hidden="true"
              title={t(`workouts:No next ${dataType}`)}
            />
          )}
        </div>
      </div>
    </div>
  )
}
