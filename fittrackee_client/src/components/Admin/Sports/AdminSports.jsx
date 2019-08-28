import React from 'react'
import { connect } from 'react-redux'

import { getOrUpdateData } from '../../../actions'
import AdminPage from '../generic/AdminPage'

class AdminSports extends React.Component {
  componentDidMount() {
    this.props.loadSports()
  }
  render() {
    const { sports } = this.props

    return (
      <div>
        <AdminPage data={sports} target="sports" />
      </div>
    )
  }
}

export default connect(
  state => ({
    sports: state.sports,
    user: state.user,
  }),
  dispatch => ({
    loadSports: () => {
      dispatch(getOrUpdateData('getData', 'sports'))
    },
  })
)(AdminSports)
