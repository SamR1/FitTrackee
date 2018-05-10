import React from 'react'
import { connect } from 'react-redux'

import ActivityAddOrEdit from './ActivityAddOrEdit'


function ActivityAdd (props) {
  const { message, sports } = props
  return (
    <div>
      <ActivityAddOrEdit
        activity={null}
        message={message}
        sports={sports}
      />
    </div>
  )
}

export default connect(
  state => ({
    message: state.message,
    sports: state.sports.data,
    user: state.user,
  }),
)(ActivityAdd)
