import React from 'react'
import { Link } from 'react-router-dom'

import { apiUrl } from '../../utils'

export default function ActivityCard (props) {
  const { activity, sports } = props

  return (
    <div className="card activity-card text-center">
      <div className="card-header">
        <Link to={`/activities/${activity.id}`}>
        {sports.filter(sport => sport.id === activity.sport_id)
               .map(sport => sport.label)} -{' '}
        {activity.activity_date}
        </Link>
      </div>
      <div className="card-body">
        <div className="row">
          {activity.map && (
            <div className="col">
              <img
                alt="Map"
                src={`${apiUrl}activities/map/${activity.map}` +
                     `?${Date.now()}`}
                className="img-fluid"
              />
            </div>
          )}
          <div className="col">
            <p>
              <i className="fa fa-calendar" aria-hidden="true" />{' '}
              Start at {activity.activity_date}
            </p>
            <p>
              <i className="fa fa-clock-o" aria-hidden="true" />{' '}
              Duration: {activity.duration}
              {activity.map ? (
                <span><br /><br /></span>
              ) : (
                ' - '
              )}
              <i className="fa fa-road" aria-hidden="true" />{' '}
              Distance: {activity.distance} km
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
