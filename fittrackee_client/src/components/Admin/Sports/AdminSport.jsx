import React from 'react'
import { connect } from 'react-redux'

import { getOrUpdateData } from '../../../actions'
import AdminDetail from '../generic/AdminDetail'

class AdminSports extends React.Component {
  componentDidMount() {
    this.props.loadSport(this.props.match.params.sportId)
  }
  componentWillUnmount() {
    // reload all Sports
    this.props.loadSport(null)
  }
  render() {
    const { sports } = this.props

    return (
      <div>
        <AdminDetail results={sports} target="sports" />
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
      dispatch(getOrUpdateData('getData', 'sports', { id: sportId }))
    },
  })
)(AdminSports)
