import React from 'react'
import { connect } from 'react-redux'

import { getData } from '../../../actions/index'
import AdminDetail from '../generic/AdminDetail'

class AdminSports extends React.Component {
  componentDidMount() {
    this.props.loadSport(
      this.props.location.pathname.replace('/admin/sport/', '')
    )
  }
  render() {
    const { sports } = this.props

    return (
      <div>
        <AdminDetail
          results={sports}
          target="sports"
        />
      </div>
    )
  }
}

export default connect(
  state => ({
    sports: state.sports.data,
    user: state.user,
  }),
  dispatch => ({
    loadSport: sportId => {
      dispatch(getData('sports', sportId))
    },
  })
)(AdminSports)
