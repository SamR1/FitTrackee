import React from 'react'
import { connect } from 'react-redux'

import { getData } from '../../../actions/index'
import AdminPage from '../generic/AdminPage'

class AdminSports extends React.Component {
  componentDidMount() {
      this.props.loadSports()
  }
  render() {
    const { sports } = this.props

    return (
      <div>
        <AdminPage
          data={sports}
          detailLink="sport"
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
    loadSports: () => {
      dispatch(getData('sports'))
    },
  })
)(AdminSports)
