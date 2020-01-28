import React from 'react'
import { Link } from 'react-router-dom'

import { recordsLabels } from '../../utils/activities'

export default function CalendarActivity(props) {
  const { activity, isDisabled, isMore, sportImg } = props
  return (
    <Link
      className={`calendar-activity${isMore}`}
      to={`/activities/${activity.id}`}
    >
      <>
        <img
          alt="activity sport logo"
          className={`activity-sport ${isDisabled}`}
          src={sportImg}
          title={activity.title}
        />
        {activity.records.length > 0 && (
          <sup>
            <i
              className="fa fa-trophy custom-fa-small"
              aria-hidden="true"
              title={activity.records.map(
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
