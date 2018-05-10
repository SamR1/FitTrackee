import React from 'react'
import { Helmet } from 'react-helmet'
import { connect } from 'react-redux'

import ActivityMap from './ActivityMap'
import CustomModal from './../Others/CustomModal'
import { getData } from '../../actions/index'
import { deleteActivity } from '../../actions/activities'

class ActivityDisplay extends React.Component {
  constructor(props, context) {
    super(props, context)
    this.state = {
      displayModal: false,
    }
  }

  componentDidMount() {
    this.props.loadActivity(
      this.props.location.pathname.replace('/activities/', '')
    )
  }

  render() {
    const { activities, message, onDeleteActivity, sports } = this.props
    const { displayModal } = this.state
    const [activity] = activities
    return (
      <div>
        <Helmet>
          <title>mpwo - Activity</title>
        </Helmet>
        <h1 className="page-title">
            Activity
        </h1>
        {message ? (
          <code>{message}</code>
        ) : (
          <div className="container">
            { displayModal &&
            <CustomModal
              title="Confirmation"
              text="Are you sure you want to delete this activity?"
              confirm={() => {
                onDeleteActivity(activity.id)
                this.setState({ displayModal: false })
              }}
              close={() => this.setState({ displayModal: false })}
            />}
          {activity && sports.length > 0 && (
            <div className="row">
            <div className="col-md-6">
              <div className="card">
                <div className="card-header">
                  {sports.filter(sport => sport.id === activity.sport_id)
                         .map(sport => sport.label)} -{' '}
                  {activity.activity_date}{' '}
                  <i className="fa fa-edit" aria-hidden="true" />{' '}
                  <i
                    className="fa fa-trash"
                    aria-hidden="true"
                    onClick={() => this.setState({ displayModal: true })}
                  />{' '}
                </div>
                <div className="card-body">
                  <p>
                    <i className="fa fa-calendar" aria-hidden="true" />{' '}
                    Start at {activity.activity_date}
                  </p>
                  <p>
                    <i className="fa fa-clock-o" aria-hidden="true" />{' '}
                    Duration: {activity.duration} {' '}
                    {activity.pauses !== '0:00:00' &&
                     activity.pauses !== null && (
                        `(pauses: ${activity.pauses})`
                    )}
                  </p>
                  <p>
                    <i className="fa fa-road" aria-hidden="true" />{' '}
                    Distance: {activity.distance} km</p>
                  <p>
                    <i className="fa fa-tachometer" aria-hidden="true" />
                    {' '}
                    Average speed: {activity.ave_speed} km/h -{' '}
                    Max speed : {activity.max_speed} km/h
                  </p>
                  {activity.min_alt && activity.max_alt && (
                  <p><i className="fi-mountains" />{' '}
                    Min altitude: {activity.min_alt}m -{' '}
                    Max altitude: {activity.max_alt}m
                  </p>
                  )}
                  {activity.ascent && activity.descent && (
                  <p><i className="fa fa-location-arrow" />{' '}
                    Ascent: {activity.ascent}m -{' '}
                    Descent: {activity.descent}m
                  </p>
                  )}
                </div>
              </div>
            </div>
            <div className="col-md-6">
              <div className="card">
                <div className="card-header">
                  Map
                </div>
                <div className="card-body">
                  {activity.with_gpx ? (
                    <ActivityMap activity={activity} />
                  ) : (
                    'No map'
                  )}
                </div>
              </div>
            </div>
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
    onDeleteActivity: activityId => {
      dispatch(deleteActivity(activityId))
    },
    loadActivity: activityId => {
      dispatch(getData('activities', activityId))
      dispatch(getData('sports'))
    },
  })
)(ActivityDisplay)
