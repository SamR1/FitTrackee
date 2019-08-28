import React from 'react'
import { Helmet } from 'react-helmet'
import { connect } from 'react-redux'
import { Link } from 'react-router-dom'

import ActivitiesFilter from './ActivitiesFilter'
import ActivitiesList from './ActivitiesList'
import { getOrUpdateData } from '../../actions'
import { getMoreActivities } from '../../actions/activities'

class Activities extends React.Component {
  constructor(props, context) {
    super(props, context)
    this.state = {
      params: {
        page: 1,
        per_page: 10,
      },
    }
  }

  componentDidMount() {
    this.props.loadActivities(this.state.params)
  }

  setParams(e) {
    const { params } = this.state
    if (e.target.value === '') {
      delete params[e.target.name]
    } else {
      params[e.target.name] = e.target.value
    }
    params.page = 1
    this.setState(params)
  }
  render() {
    const {
      activities,
      loadActivities,
      loadMoreActivities,
      message,
      sports,
      user,
    } = this.props
    const { params } = this.state
    const paginationEnd =
      activities.length > 0
        ? activities[activities.length - 1].previous_activity === null
        : true
    return (
      <div>
        <Helmet>
          <title>FitTrackee - Workouts</title>
        </Helmet>
        {message ? (
          <code>{message}</code>
        ) : (
          <div className="container history">
            <div className="row">
              <div className="col-md-3">
                <ActivitiesFilter
                  sports={sports}
                  loadActivities={() => loadActivities(params)}
                  updateParams={e => this.setParams(e)}
                />
              </div>
              <div className="col-md-9 activities-result">
                <ActivitiesList
                  activities={activities}
                  sports={sports}
                  user={user}
                />
                {!paginationEnd && (
                  <input
                    type="submit"
                    className="btn btn-default btn-md btn-block"
                    value="Load more activities"
                    onClick={() => {
                      params.page += 1
                      loadMoreActivities(params)
                      this.setState(params)
                    }}
                  />
                )}
                {activities.length === 0 && (
                  <div className="card text-center">
                    <div className="card-body">
                      No workouts.{' '}
                      <Link to={{ pathname: '/activities/add' }}>
                        Upload one !
                      </Link>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
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
    loadActivities: params => {
      dispatch(getOrUpdateData('getData', 'activities', params))
    },
    loadMoreActivities: params => {
      dispatch(getMoreActivities(params))
    },
  })
)(Activities)
