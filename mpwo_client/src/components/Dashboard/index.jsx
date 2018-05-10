import React from 'react'
import { Helmet } from 'react-helmet'
import { connect } from 'react-redux'

import ActivityCard from './ActivityCard'
import Statistics from './Statistics'
import { getData } from '../../actions/index'

class DashBoard extends React.Component {
  componentDidMount() {
    this.props.loadActivities()
  }

  render() {
    const { activities, sports } = this.props
    return (
      <div>
        <Helmet>
          <title>mpwo - Dashboard</title>
        </Helmet>
        <h1 className="page-title">Dashboard</h1>
        {activities.length > 0 ? (
          <div className="container">
            <div className="row">
              <div className="col-md-6">
                {activities.map(activity => (
                  <ActivityCard
                    activity={activity}
                    key={activity.id}
                    sports={sports}
                  />
                ))}
              </div>
              <div className="col-md-6">
                <Statistics />
              </div>
            </div>
          </div>
        ) : (
          'No activities for now'
        )}
      </div>
    )
  }
}

export default connect(
  state => ({
    activities: state.activities.data,
    message: state.message,
    sports: state.sports.data,
    user: state.user,
  }),
  dispatch => ({
    loadActivities: () => {
      dispatch(getData('activities'))
      dispatch(getData('sports'))
    },
  })
)(DashBoard)
