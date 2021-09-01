import React from 'react'
import { Link } from 'react-router-dom'

export default class NoWorkouts extends React.PureComponent {
  render() {
    const { t } = this.props
    return (
      <div className="card text-center">
        <div className="card-body">
          {t('common:No workouts.')}{' '}
          <Link to={{ pathname: '/workouts/add' }}>
            {t('dashboard:Upload one !')}
          </Link>
        </div>
      </div>
    )
  }
}
