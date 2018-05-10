import React from 'react'
import { Helmet } from 'react-helmet'
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
        <Helmet>
          <title>mpwo - Edit activity</title>
        </Helmet>
        <br /><br />
        {message && (
          <code>{message}</code>
        )}
        {sports.length > 0 && (
          <ActivityAddOrEdit
            activity={activity}
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
      dispatch(getData('sports'))
      dispatch(getData('activities', activityId))
    },
  })
)(ActivityEdit)
