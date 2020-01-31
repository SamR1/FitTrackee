import { format } from 'date-fns'
import React from 'react'
import { Link } from 'react-router-dom'

import StaticMap from '../Common/StaticMap'
import { getDateWithTZ } from '../../utils'

export default class ActivitiesList extends React.PureComponent {
  render() {
    const { activities, loading, sports, t, user } = this.props
    return (
      <div className="card  activity-card">
        <div className="card-body">
          <table className="table">
            <thead>
              <tr>
                <th scope="col" />
                <th scope="col">{t('common:Workout')}</th>
                <th scope="col">{t('activities:Date')}</th>
                <th scope="col">{t('activities:Distance')}</th>
                <th scope="col">{t('activities:Duration')}</th>
                <th scope="col">{t('activities:Ave. speed')}</th>
                <th scope="col">{t('activities:Max. speed')}</th>
              </tr>
            </thead>
            <tbody>
              {!loading &&
                sports &&
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
          {loading && <div className="loader" />}
        </div>
      </div>
    )
  }
}
