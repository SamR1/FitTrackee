import React from 'react'
import { Link } from 'react-router-dom'

import { formatActivityDate, getDateWithTZ } from '../../../utils'


export default function ActivityCardHeader(props) {
  const { activity, displayModal, sport, title, user } = props
  const activityDate = activity
    ? formatActivityDate(
        getDateWithTZ(activity.activity_date, user.timezone)
      )
    : null
  return (
    <div className="container">
      <div className="row">
        <div className="col-auto">
          {activity.previous_activity ? (
            <Link
              className="unlink"
              to={`/activities/${activity.previous_activity}`}
            >
              <i
                className="fa fa-chevron-left"
                aria-hidden="true"
                title="See previous activity"
              />
            </Link>
          ) : (
            <i
              className="fa fa-chevron-left inactive-link"
              aria-hidden="true"
              title="No previous activity"
            />
          )}
        </div>
        <div className="col-auto col-activity-logo">
          <img
            className="sport-img-medium"
            src={sport.img}
            alt="sport logo"
          />
        </div>
        <div className="col">
          {title}{' '}
          <Link
            className="unlink"
            to={`/activities/${activity.id}/edit`}
          >
            <i
              className="fa fa-edit custom-fa"
              aria-hidden="true"
              title="Edit activity"
            />
          </Link>
          <i
            className="fa fa-trash custom-fa"
            aria-hidden="true"
            onClick={() => displayModal(true)}
            title="Delete activity"
          /><br />
          {activityDate && (
            <span className="activity-date">
          {`${activityDate.activity_date} - ${activityDate.activity_time}`}
        </span>
          )}
        </div>
        <div className="col-auto">
          {activity.next_activity ? (
            <Link
              className="unlink"
              to={`/activities/${activity.next_activity}`}
            >
              <i
                className="fa fa-chevron-right"
                aria-hidden="true"
                title="See next activity"
              />
            </Link>
          ) : (
            <i
              className="fa fa-chevron-right inactive-link"
              aria-hidden="true"
              title="No next activity"
            />
          )}
        </div>
      </div>
    </div>
  )
}
