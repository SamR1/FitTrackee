import React from 'react'
import { Helmet } from 'react-helmet'
import { connect } from 'react-redux'

import ActivityCardHeader from './ActivityCardHeader'
import ActivityCharts from './ActivityCharts'
import ActivityDetails from './ActivityDetails'
import ActivityMap from './ActivityMap'
import CustomModal from './../../Others/CustomModal'
import { getData } from '../../../actions'
import { deleteActivity } from '../../../actions/activities'

class ActivityDisplay extends React.Component {
  constructor(props, context) {
    super(props, context)
    this.state = {
      displayModal: false,
    }
  }

  componentDidMount() {
    this.props.loadActivity(this.props.match.params.activityId)
  }

  componentDidUpdate(prevProps) {
    if (prevProps.match.params.activityId !==
      this.props.match.params.activityId) {
      this.props.loadActivity(this.props.match.params.activityId)
    }
  }

  displayModal(value) {
    this.setState({ displayModal: value })
  }

  render() {
    const { activities, message, onDeleteActivity, sports } = this.props
    const { displayModal } = this.state
    const [activity] = activities
    const title = activity ? activity.title : 'Activity'
    const [sport] = activity
      ? sports.filter(s => s.id === activity.sport_id)
      : []

    return (
      <div className="activity-page">
        <Helmet>
          <title>mpwo - {title}</title>
        </Helmet>
        {message ? (
          <code>{message}</code>
        ) : (
          <div className="container">
            {displayModal &&
            <CustomModal
              title="Confirmation"
              text="Are you sure you want to delete this activity?"
              confirm={() => {
                onDeleteActivity(activity.id)
                this.displayModal(false)
              }}
              close={() => this.displayModal(false)}
            />}
            {activity && sport && activities.length === 1 && (
              <div>
                <div className="row">
                  <div className="col">
                    <div className="card">
                      <div className="card-header">
                        <ActivityCardHeader
                          activity={activity}
                          sport={sport}
                          title={title}
                          displayModal={() => this.displayModal(true)}
                        />
                      </div>
                      <div className="card-body">
                        <div className="row">
                          {activity.with_gpx && (
                            <div className="col-8">
                              <ActivityMap activity={activity} />
                            </div>
                          )}
                          <div className="col">
                            <ActivityDetails activity={activity} />
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
                {activity.with_gpx && (
                  <div className="row">
                    <div className="col">
                      <div className="card">
                        <div className="card-body">
                          <div className="row">
                            <div className="col">
                              <div className="chart-title">Chart</div>
                              <ActivityCharts activity={activity} />
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            )}
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
    loadActivity: activityId => {
      dispatch(getData('activities', { id: activityId }))
    },
    onDeleteActivity: activityId => {
      dispatch(deleteActivity(activityId))
    },
  })
)(ActivityDisplay)
