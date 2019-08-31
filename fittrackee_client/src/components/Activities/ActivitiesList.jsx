import { format } from 'date-fns'
import React from 'react'
import { Link } from 'react-router-dom'

import StaticMap from '../Common/StaticMap'
import { getDateWithTZ } from '../../utils'

export default class ActivitiesList extends React.PureComponent {
  render() {
    const { activities, sports, user } = this.props
    return (
      <div className="card  activity-card">
        <div className="card-body">
          <table className="table">
            <thead>
              <tr>
                <th scope="col" />
                <th scope="col">Workout</th>
                <th scope="col">Date</th>
                <th scope="col">Distance</th>
                <th scope="col">Duration</th>
                <th scope="col">Ave. speed</th>
                <th scope="col">Max. speed</th>
              </tr>
            </thead>
            <tbody>
              {sports &&
                activities.map((activity, idx) => (
                  // eslint-disable-next-line react/no-array-index-key
                  <tr key={idx}>
                    <td>
                      <img
                        className="activity-sport"
                        src={sports
                          .filter(s => s.id === activity.sport_id)
                          .map(s => s.img)}
                        alt="activity sport logo"
                      />
                    </td>
                    <td className="activity-title">
                      <Link to={`/activities/${activity.id}`}>
                        {activity.title}
                      </Link>
                      {activity.map && (
                        <StaticMap activity={activity} display="list" />
                      )}
                    </td>
                    <td>
                      {format(
                        getDateWithTZ(activity.activity_date, user.timezone),
                        'dd/MM/yyyy HH:mm'
                      )}
                    </td>
                    <td className="text-right">
                      {Number(activity.distance).toFixed(2)} km
                    </td>
                    <td className="text-right">{activity.moving}</td>
                    <td className="text-right">{activity.ave_speed} km/h</td>
                    <td className="text-right">{activity.max_speed} km/h</td>
                  </tr>
                ))}
            </tbody>
          </table>
        </div>
      </div>
    )
  }
}
