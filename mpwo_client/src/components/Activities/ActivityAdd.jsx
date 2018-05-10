import React from 'react'
import { connect } from 'react-redux'

import ActivityAddOrEdit from './ActivityAddOrEdit'
import { getData } from '../../actions/index'


class ActivityAdd extends React.Component {
  componentDidMount() {
      this.props.loadSports()
  }

  render() {
    const { message, sports } = this.props
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
}

export default connect(
  state => ({
    message: state.message,
    sports: state.sports.data,
    user: state.user,
  }),
  dispatch => ({
    loadSports: () => {
      dispatch(getData('sports'))
    },
  })
)(ActivityAdd)
