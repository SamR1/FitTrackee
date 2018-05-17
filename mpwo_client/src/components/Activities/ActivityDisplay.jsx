import React from 'react'
import { Helmet } from 'react-helmet'
import { connect } from 'react-redux'
import { Link } from 'react-router-dom'

import ActivityMap from './ActivityMap'
import CustomModal from './../Others/CustomModal'
import { getData } from '../../actions'
import { deleteActivity } from '../../actions/activities'
import { formatActivityDate } from '../../utils'

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

  render() {
    const { activities, message, onDeleteActivity, sports } = this.props
    const { displayModal } = this.state
    const [activity] = activities
    const title = activity ? activity.title : 'Activity'
    const [sport] = activity
      ? sports.filter(s => s.id === activity.sport_id)
      : []
    const activityDate = activity
      ? formatActivityDate(activity.activity_date)
      : null
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
                this.setState({ displayModal: false })
              }}
              close={() => this.setState({ displayModal: false })}
            />}
            {activity && sport && activities.length === 1 && (
              <div className="row">
                <div className="col">
                  <div className="card">
                    <div className="card-header">
                      <div className="row">
                        <div className="col-auto">
                          {activity.previous_activity ? (
                            <Link
                              className="unlink"
                              to={`/activities/${activity.previous_activity}`}
                            >
                              <i
                                className="fa fa-chevron-left"
                                aria-hidden="true"
                              />
                            </Link>
                          ) : (
                              <i
                                className="fa fa-chevron-left inactive-link"
                                aria-hidden="true"
                              />
                          )}
                        </div>
                        <div className="col-auto col-activity-logo">
                          <img
                            className="sport-img-medium"
                            src={sport.img}
                            alt="sport logo"
                          />
                        </div>
                        <div className="col">
                          {title}{' '}
                          <Link
                            className="unlink"
                            to={`/activities/${activity.id}/edit`}
                          >
                            <i
                              className="fa fa-edit custom-fa"
                              aria-hidden="true"
                            />
                          </Link>
                          <i
                            className="fa fa-trash custom-fa"
                            aria-hidden="true"
                            onClick={
                              () => this.setState({ displayModal: true })
                            }
                          /><br />
                          {activityDate && (
                            <span className="activity-date">
                          {`${activityDate.activity_date} - ${
                            activityDate.activity_time}`}
                        </span>
                          )}
                        </div>
                        <div className="col-auto">
                          {activity.next_activity ? (
                            <Link
                              className="unlink"
                              to={`/activities/${activity.next_activity}`}
                            >
                              <i
                                className="fa fa-chevron-right"
                                aria-hidden="true"
                              />
                            </Link>
                          ) : (
                              <i
                                className="fa fa-chevron-right inactive-link"
                                aria-hidden="true"
                              />
                          )}
                        </div>
                      </div>
                    </div>
                    <div className="card-body">
                      <div className="row">
                        {activity.with_gpx && (
                          <div className="col-8">
                            <ActivityMap activity={activity} />
                          </div>
                        )}
                        <div className="col">
                          <p>
                            <i
                              className="fa fa-clock-o custom-fa"
                              aria-hidden="true"
                            />
                            Duration: {activity.duration}
                            {activity.records.find(r => r.record_type === 'LD'
                            ) && (
                              <sup>
                                <i
                                  className="fa fa-trophy custom-fa"
                                  aria-hidden="true"
                                />
                              </sup>
                            )} {' '}
                            {activity.pauses !== '0:00:00' &&
                            activity.pauses !== null && (
                              `(pauses: ${activity.pauses})`
                            )}
                          </p>
                          <p>
                            <i
                              className="fa fa-road custom-fa"
                              aria-hidden="true"
                            />
                            Distance: {activity.distance} km
                            {activity.records.find(r => r.record_type === 'FD'
                            ) && (
                              <sup>
                                <i
                                  className="fa fa-trophy custom-fa"
                                  aria-hidden="true"
                                />
                              </sup>
                            )}
                          </p>
                          <p>
                            <i
                              className="fa fa-tachometer custom-fa"
                              aria-hidden="true"
                            />
                            Average speed: {activity.ave_speed} km/h
                            {activity.records.find(r => r.record_type === 'AS'
                            ) && (
                              <sup>
                                <i
                                  className="fa fa-trophy custom-fa"
                                  aria-hidden="true"
                                />
                              </sup>
                            )}
                            <br />
                            Max speed : {activity.max_speed} km/h
                            {activity.records.find(r => r.record_type === 'MS'
                            ) && (
                              <sup>
                                <i
                                  className="fa fa-trophy custom-fa"
                                  aria-hidden="true"
                                />
                              </sup>
                            )}
                          </p>
                          {activity.min_alt && activity.max_alt && (
                            <p>
                              <i className="fi-mountains custom-fa" />
                              Min altitude: {activity.min_alt}m
                              <br />
                              Max altitude: {activity.max_alt}m
                            </p>
                          )}
                          {activity.ascent && activity.descent && (
                            <p>
                              <i className="fa fa-location-arrow custom-fa" />
                              Ascent: {activity.ascent}m
                              <br />
                              Descent: {activity.descent}m
                            </p>
                          )}
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
      dispatch(getData('activities', activityId))
    },
    onDeleteActivity: activityId => {
      dispatch(deleteActivity(activityId))
    },
  })
)(ActivityDisplay)
