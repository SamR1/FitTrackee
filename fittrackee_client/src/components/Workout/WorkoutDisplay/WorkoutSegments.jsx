import React from 'react'
import { Link } from 'react-router-dom'

import { convert } from '../../../utils/conversions'

export default function WorkoutSegments(props) {
  const { segments, t } = props
  return (
    <div className="row">
      <div className="col">
        <div className="card workout-card">
          <div className="card-body">
            {t('workouts:Segments')}
            <div className="workout-segments">
              <ul>
                {segments.map((segment, index) => (
                  <li
                    className="workout-segments-list"
                    // eslint-disable-next-line react/no-array-index-key
                    key={`segment-${index}`}
                  >
                    <Link
                      to={`/workouts/${segment.workout_id}/segment/${
                        index + 1
                      }`}
                    >
                      {t('workouts:segment')} {index + 1}
                    </Link>{' '}
                    ({t('workouts:distance')}:{' '}
                    {convert(segment.distance, t('common:km'))}:{' '}
                    {t('common:km')}, {t('workouts:duration')}:{' '}
                    {segment.duration})
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
