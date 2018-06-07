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
      <div className="container dashboard">
        <div className="row">
          <div className="col-2" />
          <div className="card col-8">
            <div className="card-body">
              <div className="text-center">
                You are now logged out.
                Click <Link to="/login">here</Link> to log back in.
              </div>
            </div>
          </div>
          <div className="col-2" />
        </div>
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
