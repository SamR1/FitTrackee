import React from 'react'
import { Link } from 'react-router-dom'

import { recordsLabels } from '../../utils/workouts'

export default function CalendarWorkout(props) {
  const { isDisabled, isMore, sportImg, workout } = props
  return (
    <Link
      className={`calendar-workout${isMore}`}
      to={`/workouts/${workout.id}`}
    >
      <>
        <img
          alt="workout sport logo"
          className={`workout-sport ${isDisabled}`}
          src={sportImg}
          title={workout.title}
        />
        {workout.records.length > 0 && (
          <sup>
            <i
              className="fa fa-trophy custom-fa-small"
              aria-hidden="true"
              title={workout.records.map(
                rec =>
                  ` ${
                    recordsLabels.filter(
                      r => r.record_type === rec.record_type
                    )[0].label
                  }`
              )}
            />
          </sup>
        )}
      </>
    </Link>
  )
}
