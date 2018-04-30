import React from 'react'
import { connect } from 'react-redux'

import { getData } from '../../actions/index'
import AdminPage from './AdminPage'

class AdminSports extends React.Component {
  componentDidMount() {
      this.props.loadSport()
  }
  render() {
    const { sports } = this.props
    return (
      <div>
        <AdminPage
          data={sports}
          target="sports"
        />
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
    loadSport: () => {
      dispatch(getData('sports'))
    },
  })
)(AdminSports)
