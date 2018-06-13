import { format } from 'date-fns'
import React from 'react'
import { Link } from 'react-router-dom'

import { apiUrl, getDateWithTZ } from '../../utils'

export default function ActivityCard (props) {
  const { activity, sports, user } = props

  return (
    <div className="card activity-card text-center">
      <div className="card-header">
        <Link to={`/activities/${activity.id}`}>
        {sports.filter(sport => sport.id === activity.sport_id)
               .map(sport => sport.label)} -{' '}
        {format(
          getDateWithTZ(activity.activity_date, user.timezone),
          'DD/MM/YYYY HH:mm'
        )}
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
              <div className="map-attribution text-right">
                <div>
                  <span className="map-attribution-text">
                    ©
                  </span>
                  <a
                    className="map-attribution-text"
                    href="http://www.openstreetmap.org/copyright"
                    target="_blank"
                    rel="noopener noreferrer"
                  >
                    OpenStreetMap
                  </a>
                </div>
              </div>
            </div>
          )}
          <div className="col">
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
