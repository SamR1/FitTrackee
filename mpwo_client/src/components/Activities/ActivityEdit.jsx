import React from 'react'
import { connect } from 'react-redux'

import ActivityAddOrEdit from './ActivityAddOrEdit'
import { getData } from '../../actions/index'


class ActivityEdit extends React.Component {
  componentDidMount() {
    this.props.loadActivity(
      this.props.match.params.activityId
    )
  }

  render() {
    const { activities, message, sports } = this.props
    const [activity] = activities
    return (
      <div>
        {sports.length > 0 && (
          <ActivityAddOrEdit
            activity={activity}
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
    activities: state.activities.data,
    message: state.message,
    sports: state.sports.data,
    user: state.user,
  }),
  dispatch => ({
    loadActivity: activityId => {
      dispatch(getData('activities', activityId))
    },
  })
)(ActivityEdit)
