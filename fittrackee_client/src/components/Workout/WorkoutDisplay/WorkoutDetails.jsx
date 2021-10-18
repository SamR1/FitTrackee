import React from 'react'

import WorkoutWeather from './WorkoutWeather'
import { convert } from '../../../utils/conversions'

export default function WorkoutDetails(props) {
  const { t, workout } = props
  const withPauses = workout.pauses !== '0:00:00' && workout.pauses !== null
  return (
    <div className="workout-details">
      <p>
        <i className="fa fa-clock-o custom-fa" aria-hidden="true" />
        {t('workouts:Duration')}: {workout.moving}
        {workout.records &&
          workout.records.find(record => record.record_type === 'LD') && (
            <sup>
              <i className="fa fa-trophy custom-fa" aria-hidden="true" />
            </sup>
          )}
        {withPauses && (
          <span>
            <br />({t('workouts:pauses')}: {workout.pauses},{' '}
            {t('workouts:total duration')}: {workout.duration})
          </span>
        )}
      </p>
      <p>
        <i className="fa fa-road custom-fa" aria-hidden="true" />
        {t('workouts:Distance')}: {convert(workout.distance, t('common:km'))}{' '}
        {t('common:km')}
        {workout.records &&
          workout.records.find(record => record.record_type === 'FD') && (
            <sup>
              <i className="fa fa-trophy custom-fa" aria-hidden="true" />
            </sup>
          )}
      </p>
      <p>
        <i className="fa fa-tachometer custom-fa" aria-hidden="true" />
        {t('workouts:Average speed')}:{' '}
        {convert(workout.ave_speed, t('common:km'))} {t('common:km')}/h
        {workout.records &&
          workout.records.find(record => record.record_type === 'AS') && (
            <sup>
              <i className="fa fa-trophy custom-fa" aria-hidden="true" />
            </sup>
          )}
        <br />
        {t('workouts:Max. speed')}: {convert(workout.max_speed, t('common:km'))}{' '}
        {t('common:km')}/h
        {workout.records &&
          workout.records.find(record => record.record_type === 'MS') && (
            <sup>
              <i className="fa fa-trophy custom-fa" aria-hidden="true" />
            </sup>
          )}
      </p>
      {workout.min_alt && workout.max_alt && (
        <p>
          <i className="fi-mountains custom-fa" />
          {t('workouts:Min. altitude')}:
          {convert(workout.min_alt, t('common:m'))} {t('common:m')}
          <br />
          {t('workouts:Max. altitude')}:{' '}
          {convert(workout.max_alt, t('common:m'))} {t('common:m')}
        </p>
      )}
      {workout.ascent && workout.descent && (
        <p>
          <i className="fa fa-location-arrow custom-fa" />
          {t('workouts:Ascent')}: {convert(workout.ascent, t('common:m'))}{' '}
          {t('common:m')}
          <br />
          {t('workouts:Descent')}: {convert(workout.descent, t('common:m'))}{' '}
          {t('common:m')}
        </p>
      )}
      <WorkoutWeather workout={workout} t={t} />
    </div>
  )
}
