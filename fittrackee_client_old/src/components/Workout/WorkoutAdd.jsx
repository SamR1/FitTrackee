import React from 'react'
import { connect } from 'react-redux'

import WorkoutAddOrEdit from './WorkoutAddOrEdit'

function WorkoutAdd(props) {
  const { message, sports } = props
  return (
    <div>
      <WorkoutAddOrEdit workout={null} message={message} sports={sports} />
    </div>
  )
}

export default connect(state => ({
  message: state.message,
  sports: state.sports.data,
  user: state.user,
}))(WorkoutAdd)
