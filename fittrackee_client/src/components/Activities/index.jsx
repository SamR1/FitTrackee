import React from 'react'
import { Helmet } from 'react-helmet'
import { connect } from 'react-redux'

import ActivitiesFilter from './ActivitiesFilter'
import ActivitiesList from './ActivitiesList'
import { getData } from '../../actions'
import { getMoreActivities } from '../../actions/activities'


class Activities extends React.Component {
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
    const { activities, loadMoreActivities, message, sports } = this.props
    const { page } = this.state
    const paginationEnd = activities.length > 0
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
                />
              </div>
              <div className="col-md-9">
                <ActivitiesList
                  activities={activities}
                  sports={sports}
                />
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
  }),
  dispatch => ({
    loadActivities: () => {
      dispatch(getData('activities', { page: 1, per_page: 10 }))
      dispatch(getData('records'))
    },
    loadMoreActivities: page => {
      dispatch(getMoreActivities({ page, per_page: 10 }))
    },
  })
)(Activities)
