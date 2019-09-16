import React from 'react'
import { Link } from 'react-router-dom'

export default class NoActivities extends React.PureComponent {
  render() {
    const { t } = this.props
    return (
      <div className="card text-center">
        <div className="card-body">
          {t('common:No workouts.')}{' '}
          <Link to={{ pathname: '/activities/add' }}>
            {t('dashboard:Upload one !')}
          </Link>
        </div>
      </div>
    )
  }
}
