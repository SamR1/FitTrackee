import React from 'react'
import { Helmet } from 'react-helmet'
import { withTranslation } from 'react-i18next'
import { connect } from 'react-redux'

import ActivityCardHeader from './ActivityCardHeader'
import ActivityCharts from './ActivityCharts'
import ActivityDetails from './ActivityDetails'
import ActivityMap from './ActivityMap'
import ActivityNoMap from './ActivityNoMap'
import ActivityNotes from './ActivityNotes'
import ActivitySegments from './ActivitySegments'
import CustomModal from '../../Common/CustomModal'
import Message from '../../Common/Message'
import { getOrUpdateData } from '../../../actions'
import { deleteActivity } from '../../../actions/activities'

class ActivityDisplay extends React.Component {
  constructor(props, context) {
    super(props, context)
    this.state = {
      displayModal: false,
      coordinates: {
        latitude: null,
        longitude: null,
      },
    }
  }

  componentDidMount() {
    this.props.loadActivity(this.props.match.params.activityId)
  }

  componentDidUpdate(prevProps) {
    if (
      prevProps.match.params.activityId !== this.props.match.params.activityId
    ) {
      this.props.loadActivity(this.props.match.params.activityId)
    }
  }

  displayModal(value) {
    this.setState(prevState => ({
      ...prevState,
      displayModal: value,
    }))
  }

  updateCoordinates(activePayload) {
    const coordinates =
      activePayload && activePayload.length > 0
        ? {
            latitude: activePayload[0].payload.latitude,
            longitude: activePayload[0].payload.longitude,
          }
        : {
            latitude: null,
            longitude: null,
          }
    this.setState(prevState => ({
      ...prevState,
      coordinates,
    }))
  }

  render() {
    const {
      activities,
      message,
      onDeleteActivity,
      sports,
      t,
      user,
    } = this.props
    const { coordinates, displayModal } = this.state
    const [activity] = activities
    const title = activity ? activity.title : 'Activity'
    const [sport] = activity
      ? sports.filter(s => s.id === activity.sport_id)
      : []
    const segmentId = parseInt(this.props.match.params.segmentId)
    const dataType = segmentId >= 0 ? 'segment' : 'activity'
    return (
      <div className="activity-page">
        <Helmet>
          <title>FitTrackee - {title}</title>
        </Helmet>
        {message ? (
          <Message message={message} t={t} />
        ) : (
          <div className="container">
            {displayModal && (
              <CustomModal
                title={t('activities:Confirmation')}
                text={t(
                  'activities:Are you sure you want to delete this activity?'
                )}
                confirm={() => {
                  onDeleteActivity(activity.id)
                  this.displayModal(false)
                }}
                close={() => this.displayModal(false)}
              />
            )}
            {activity && sport && activities.length === 1 && (
              <div>
                <div className="row">
                  <div className="col">
                    <div className="card activity-card">
                      <div className="card-header">
                        <ActivityCardHeader
                          activity={activity}
                          dataType={dataType}
                          segmentId={segmentId}
                          sport={sport}
                          t={t}
                          title={title}
                          user={user}
                          displayModal={() => this.displayModal(true)}
                        />
                      </div>
                      <div className="card-body">
                        <div className="row">
                          <div className="col-md-8">
                            {activity.with_gpx ? (
                              <ActivityMap
                                activity={activity}
                                coordinates={coordinates}
                                dataType={dataType}
                                segmentId={segmentId}
                              />
                            ) : (
                              <ActivityNoMap t={t} />
                            )}
                          </div>
                          <div className="col">
                            <ActivityDetails
                              activity={
                                dataType === 'activity'
                                  ? activity
                                  : activity.segments[segmentId - 1]
                              }
                              t={t}
                            />
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
                {activity.with_gpx && (
                  <div className="row">
                    <div className="col">
                      <div className="card activity-card">
                        <div className="card-body">
                          <div className="row">
                            <div className="col">
                              <div className="chart-title">
                                {t('activities:Chart')}
                              </div>
                              <ActivityCharts
                                activity={activity}
                                dataType={dataType}
                                segmentId={segmentId}
                                t={t}
                                updateCoordinates={e =>
                                  this.updateCoordinates(e)
                                }
                              />
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                )}
                {dataType === 'activity' && (
                  <>
                    <ActivityNotes notes={activity.notes} t={t} />
                    {activity.segments.length > 1 && (
                      <ActivitySegments segments={activity.segments} t={t} />
                    )}
                  </>
                )}
              </div>
            )}
          </div>
        )}
      </div>
    )
  }
}

export default withTranslation()(
  connect(
    state => ({
      activities: state.activities.data,
      message: state.message,
      sports: state.sports.data,
      user: state.user,
    }),
    dispatch => ({
      loadActivity: activityId => {
        dispatch(getOrUpdateData('getData', 'activities', { id: activityId }))
      },
      onDeleteActivity: activityId => {
        dispatch(deleteActivity(activityId))
      },
    })
  )(ActivityDisplay)
)
