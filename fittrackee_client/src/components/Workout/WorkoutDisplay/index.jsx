import React from 'react'
import { Helmet } from 'react-helmet'
import { withTranslation } from 'react-i18next'
import { connect } from 'react-redux'

import CustomModal from '../../Common/CustomModal'
import Message from '../../Common/Message'
import WorkoutCardHeader from './WorkoutCardHeader'
import WorkoutCharts from './WorkoutCharts'
import WorkoutDetails from './WorkoutDetails'
import WorkoutMap from './WorkoutMap'
import WorkoutNoMap from './WorkoutNoMap'
import WorkoutNotes from './WorkoutNotes'
import WorkoutSegments from './WorkoutSegments'
import { getOrUpdateData } from '../../../actions'
import { deleteWorkout } from '../../../actions/workouts'

class WorkoutDisplay extends React.Component {
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
    this.props.loadWorkout(this.props.match.params.workoutId)
  }

  componentDidUpdate(prevProps) {
    if (
      prevProps.match.params.workoutId !== this.props.match.params.workoutId
    ) {
      this.props.loadWorkout(this.props.match.params.workoutId)
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
    const { message, onDeleteWorkout, sports, t, user, workouts } = this.props
    const { coordinates, displayModal } = this.state
    const [workout] = workouts
    const title = workout ? workout.title : t('workouts:Workout')
    const [sport] = workout ? sports.filter(s => s.id === workout.sport_id) : []
    const segmentId = parseInt(this.props.match.params.segmentId)
    const dataType = segmentId >= 0 ? 'segment' : 'workout'
    return (
      <div className="workout-page">
        <Helmet>
          <title>FitTrackee - {title}</title>
        </Helmet>
        {message ? (
          <Message message={message} t={t} />
        ) : (
          <div className="container">
            {displayModal && (
              <CustomModal
                title={t('common:Confirmation')}
                text={t(
                  'workouts:Are you sure you want to delete this workout?'
                )}
                confirm={() => {
                  onDeleteWorkout(workout.id)
                  this.displayModal(false)
                }}
                close={() => this.displayModal(false)}
              />
            )}
            {workout && sport && workouts.length === 1 && (
              <div>
                <div className="row">
                  <div className="col">
                    <div className="card workout-card">
                      <div className="card-header">
                        <WorkoutCardHeader
                          workout={workout}
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
                            {workout.with_gpx ? (
                              <WorkoutMap
                                workout={workout}
                                coordinates={coordinates}
                                dataType={dataType}
                                segmentId={segmentId}
                              />
                            ) : (
                              <WorkoutNoMap t={t} />
                            )}
                          </div>
                          <div className="col">
                            <WorkoutDetails
                              workout={
                                dataType === 'workout'
                                  ? workout
                                  : workout.segments[segmentId - 1]
                              }
                              t={t}
                            />
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
                {workout.with_gpx && (
                  <div className="row">
                    <div className="col">
                      <div className="card workout-card">
                        <div className="card-body">
                          <div className="row">
                            <div className="col">
                              <div className="chart-title">
                                {t('workouts:Chart')}
                              </div>
                              <WorkoutCharts
                                workout={workout}
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
                {dataType === 'workout' && (
                  <>
                    <WorkoutNotes notes={workout.notes} t={t} />
                    {workout.segments.length > 1 && (
                      <WorkoutSegments segments={workout.segments} t={t} />
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
      workouts: state.workouts.data,
      message: state.message,
      sports: state.sports.data,
      user: state.user,
    }),
    dispatch => ({
      loadWorkout: workoutId => {
        dispatch(getOrUpdateData('getData', 'workouts', { id: workoutId }))
      },
      onDeleteWorkout: workoutId => {
        dispatch(deleteWorkout(workoutId))
      },
    })
  )(WorkoutDisplay)
)
