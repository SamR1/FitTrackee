import React from 'react'
import { connect } from 'react-redux'
import { Link } from 'react-router-dom'

import { apiUrl } from '../../utils'

class NavBar extends React.PureComponent {
  render() {
    const { user } = this.props
    return (
      <header>
        <nav className="navbar navbar-expand-lg navbar-light bg-light">
          <div className="container">
            <span className="navbar-brand">FitTrackee</span>
            <button
              className="navbar-toggler"
              type="button"
              data-toggle="collapse"
              data-target="#navbarSupportedContent"
              aria-controls="navbarSupportedContent"
              aria-expanded="false"
              aria-label="Toggle navigation"
            >
              <span className="navbar-toggler-icon" />
            </button>
            <div
              className="collapse navbar-collapse"
              id="navbarSupportedContent"
            >
              <ul className="navbar-nav mr-auto">
                <li className="nav-item">
                  <Link
                    className="nav-link"
                    to={{
                      pathname: '/',
                    }}
                  >
                    Dashboard
                  </Link>
                </li>
                {user.isAuthenticated && (
                  <li className="nav-item">
                    <Link
                      className="nav-link"
                      to={{
                        pathname: '/activities/history',
                      }}
                    >
                      Workouts
                    </Link>
                  </li>
                )}
                {user.isAuthenticated && (
                  <li className="nav-item">
                    <Link
                      className="nav-link"
                      to={{
                        pathname: '/activities/add',
                      }}
                    >
                      <strong>Add workout</strong>
                    </Link>
                  </li>
                )}
                {/* {user.admin && ( */}
                  {/* <li className="nav-item"> */}
                    {/* <Link */}
                      {/* className="nav-link" */}
                      {/* to={{ */}
                        {/* pathname: '/admin', */}
                      {/* }} */}
                    {/* > */}
                      {/* Admin */}
                    {/* </Link> */}
                  {/* </li> */}
                {/* )} */}
              </ul>
              <ul className="navbar-nav flex-row ml-md-auto d-none d-md-flex">
                {!user.isAuthenticated && (
                  <li className="nav-item">
                    <Link
                      className="nav-link"
                      to={{
                        pathname: '/register',
                      }}
                    >
                      Register
                    </Link>
                  </li>
                )}
                {!user.isAuthenticated && (
                  <li className="nav-item">
                    <Link
                      className="nav-link"
                      to={{
                        pathname: '/login',
                      }}
                    >
                      Login
                    </Link>
                  </li>
                )}
                {user.picture === true && (
                  <img
                    alt="Avatar"
                    src={`${apiUrl}users/${user.id}/picture` +
                    `?${Date.now()}`}
                    className="img-fluid App-nav-profile-img"
                  />
                )}
                {user.isAuthenticated && (
                  <li className="nav-item">
                    <Link
                      className="nav-link"
                      to={{
                        pathname: '/profile',
                      }}
                    >
                      {user.username}
                    </Link>
                  </li>
                )}
                {user.isAuthenticated && (
                  <li className="nav-item">
                    <Link
                      className="nav-link"
                      to={{
                        pathname: '/logout',
                      }}
                    >
                      Logout
                    </Link>
                  </li>
                )}
              </ul>
            </div>
          </div>
        </nav>
      </header>
    )
  }
}

export default connect(
  state => ({
    user: state.user,
  })
)(NavBar)
