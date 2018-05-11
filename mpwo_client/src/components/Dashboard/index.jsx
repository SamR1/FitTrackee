import React from 'react'
import { Helmet } from 'react-helmet'
import { connect } from 'react-redux'

import ActivityCard from './ActivityCard'
import Statistics from './Statistics'
import { getData } from '../../actions'
import { endPagination, getMoreActivities } from '../../actions/activities'

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

  componentWillUnmount() {
    this.props.resetPaginationStatus(false)
  }

  render() {
    const {
      activities, loadMoreActivities, message, paginationEnd, sports
    } = this.props
    const { page } = this.state
    return (
      <div>
        <Helmet>
          <title>mpwo - Dashboard</title>
        </Helmet>
        <h1 className="page-title">Dashboard</h1>
        {message ? (
          <code>{message}</code>
        ) : (
          activities.length > 0 ? (
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
                <div className="col-md-6">
                  <Statistics />
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
    paginationEnd: state.activities.pagination_end,
    message: state.message,
    sports: state.sports.data,
  }),
  dispatch => ({
    resetPaginationStatus: () => {
      dispatch(endPagination(false))
    },
    loadActivities: () => {
      dispatch(getData('activities', null, 1))
    },
    loadMoreActivities: page => {
      dispatch(getMoreActivities(page))
    },
  })
)(DashBoard)
