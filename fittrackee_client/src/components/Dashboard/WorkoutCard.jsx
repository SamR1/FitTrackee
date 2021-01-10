import { format } from 'date-fns'
import React from 'react'
import { Link } from 'react-router-dom'

import StaticMap from '../Common/StaticMap'
import { getDateWithTZ } from '../../utils'

export default function WorkoutCard(props) {
  const { sports, t, user, workout } = props

  return (
    <div className="card workout-card text-center">
      <div className="card-header">
        <Link to={`/workouts/${workout.id}`}>
          {sports
            .filter(sport => sport.id === workout.sport_id)
            .map(sport => t(`sports:${sport.label}`))}{' '}
          -{' '}
          {format(
            getDateWithTZ(workout.workout_date, user.timezone),
            'dd/MM/yyyy HH:mm'
          )}
        </Link>
      </div>
      <div className="card-body">
        <div className="row">
          {workout.map && (
            <div className="col">
              <StaticMap workout={workout} />
            </div>
          )}
          <div className="col">
            <p>
              <i className="fa fa-clock-o" aria-hidden="true" />{' '}
              {t('workouts:Duration')}: {workout.moving}
              {workout.map ? (
                <span>
                  <br />
                  <br />
                </span>
              ) : (
                ' - '
              )}
              <i className="fa fa-road" aria-hidden="true" />{' '}
              {t('workouts:Distance')}: {workout.distance} km
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
