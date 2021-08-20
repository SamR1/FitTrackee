import { format } from 'date-fns'
import React from 'react'
import { Link } from 'react-router-dom'

import StaticMap from '../Common/StaticMap'
import { getDateWithTZ } from '../../utils'

export default class WorkoutsList extends React.PureComponent {
  render() {
    const { loading, sports, t, user, workouts } = this.props
    return (
      <div className="card  workout-card">
        <div className="card-body">
          <table className="table">
            <thead>
              <tr>
                <th scope="col" />
                <th scope="col">{t('common:Workout')}</th>
                <th scope="col">{t('workouts:Date')}</th>
                <th scope="col">{t('workouts:Distance')}</th>
                <th scope="col">{t('workouts:Duration')}</th>
                <th scope="col">{t('workouts:Ave. speed')}</th>
                <th scope="col">{t('workouts:Max. speed')}</th>
                <th scope="col">{t('workouts:Ascent')}</th>
                <th scope="col">{t('workouts:Descent')}</th>
              </tr>
            </thead>
            <tbody>
              {!loading &&
                sports &&
                workouts.map((workout, idx) => (
                  // eslint-disable-next-line react/no-array-index-key
                  <tr key={idx}>
                    <td>
                      <span className="heading-span-absolute">
                        {t('common:Sport')}
                      </span>
                      <img
                        className="workout-sport"
                        src={sports
                          .filter(s => s.id === workout.sport_id)
                          .map(s => s.img)}
                        alt="workout sport logo"
                      />
                    </td>
                    <td className="workout-title">
                      <span className="heading-span-absolute">
                        {t('common:Workout')}
                      </span>
                      <Link to={`/workouts/${workout.id}`}>
                        {workout.title}
                      </Link>
                      {workout.map && (
                        <StaticMap workout={workout} display="list" />
                      )}
                    </td>
                    <td>
                      <span className="heading-span-absolute">
                        {t('workouts:Date')}
                      </span>
                      {format(
                        getDateWithTZ(workout.workout_date, user.timezone),
                        'dd/MM/yyyy HH:mm'
                      )}
                    </td>
                    <td className="text-right">
                      <span className="heading-span-absolute">
                        {t('workouts:Distance')}
                      </span>
                      {Number(workout.distance).toFixed(2)} km
                    </td>
                    <td className="text-right">
                      <span className="heading-span-absolute">
                        {t('workouts:Duration')}
                      </span>
                      {workout.moving}
                    </td>
                    <td className="text-right">
                      <span className="heading-span-absolute">
                        {t('workouts:Ave. speed')}
                      </span>
                      {workout.ave_speed} km/h
                    </td>
                    <td className="text-right">
                      <span className="heading-span-absolute">
                        {t('workouts:Max. speed')}
                      </span>
                      {workout.max_speed} km/h
                    </td>
                    <td className="text-right">
                      <span className="heading-span-absolute">
                        {t('workouts:Ascent')}
                      </span>
                      {workout.ascent} m
                    </td>
                    <td className="text-right">
                      <span className="heading-span-absolute">
                        {t('workouts:Descent')}
                      </span>
                      {workout.descent} m
                    </td>
                  </tr>
                ))}
            </tbody>
          </table>
          {loading && <div className="loader" />}
        </div>
      </div>
    )
  }
}
