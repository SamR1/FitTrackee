import React from 'react'
import { connect } from 'react-redux'

import WorkoutAddOrEdit from './WorkoutAddOrEdit'
import { getOrUpdateData } from '../../actions'

class WorkoutEdit extends React.Component {
  componentDidMount() {
    this.props.loadWorkout(this.props.match.params.workoutId)
  }

  render() {
    const { message, sports, workouts } = this.props
    const [workout] = workouts
    return (
      <div>
        {sports.length > 0 && (
          <WorkoutAddOrEdit
            workout={workout}
            message={message}
            sports={sports}
          />
        )}
      </div>
    )
  }
}

export default connect(
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
  })
)(WorkoutEdit)
