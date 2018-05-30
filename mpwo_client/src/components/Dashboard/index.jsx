import React from 'react'
import { Helmet } from 'react-helmet'
import { connect } from 'react-redux'

import ActivityCard from './ActivityCard'
import Records from './Records'
import Statistics from './Statistics'
import { getData } from '../../actions'
import { getMoreActivities } from '../../actions/activities'

class DashBoard extends React.Component {
  constructor(props, context) {
    super(props, context)
    this.state = {
      page: 1,
    }
  }

  componentDidMount() {
    this.props.loadActivities()
  }

  render() {
    const {
      activities, loadMoreActivities, message, records, sports
    } = this.props
    const paginationEnd = activities.length > 0
      ? activities[activities.length - 1].previous_activity === null
      : true
    const { page } = this.state
    return (
      <div>
        <Helmet>
          <title>mpwo - Dashboard</title>
        </Helmet>
        {message ? (
          <code>{message}</code>
        ) : (
          (activities.length > 0 && sports.length > 0) ? (
            <div className="container dashboard">
              <div className="row">
                <div className="col-md-4">
                  <Records records={records} sports={sports} />
                  <Statistics />
                </div>
                <div className="col-md-8">
                  {activities.map(activity => (
                    <ActivityCard
                      activity={activity}
                      key={activity.id}
                      sports={sports}
                    />
                  ))}
                  {!paginationEnd &&
                    <input
                      type="submit"
                      className="btn btn-default btn-md btn-block"
                      value="Load more activities"
                      onClick={() => {
                        loadMoreActivities(page + 1)
                        this.setState({ page: page + 1 })
                      }}
                    />
                  }
                </div>
              </div>
            </div>
        ) : (
          'No activities for now'
        ))}
      </div>
    )
  }
}

export default connect(
  state => ({
    activities: state.activities.data,
    message: state.message,
    records: state.records.data,
    sports: state.sports.data,
  }),
  dispatch => ({
    loadActivities: () => {
      dispatch(getData('activities', null, 1))
      dispatch(getData('records'))
    },
    loadMoreActivities: page => {
      dispatch(getMoreActivities(page))
    },
  })
)(DashBoard)
