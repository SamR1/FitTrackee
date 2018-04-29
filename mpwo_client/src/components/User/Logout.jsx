import React from 'react'
import { connect } from 'react-redux'
import { Link } from 'react-router-dom'

import { logout } from '../../actions/user'

class Logout extends React.Component {
  componentDidMount() {
    this.props.UserLogout()
  }
  render() {
    return (
      <div>
        <p className="App-center">
          You are now logged out.
          Click <Link to="/login">here</Link> to log back in.</p>
      </div>
    )
  }
}

export default connect(
  state => ({
    user: state.user,
  }),
  dispatch => ({
    UserLogout: () => {
      dispatch(logout())
    }
  })
)(Logout)
