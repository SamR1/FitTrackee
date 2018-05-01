import React from 'react'
import { connect } from 'react-redux'
import { Link } from 'react-router-dom'

import { apiUrl } from '../../utils'


function NavBar (props) {
  return (
    <header>
      <nav className="navbar navbar-expand-lg navbar-light bg-light">
        <span className="navbar-brand">mpwo</span>
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
        <div className="collapse navbar-collapse" id="navbarSupportedContent">
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
            {props.user.isAuthenticated && (
            <li className="nav-item">
              <Link
                className="nav-link"
                to={{
                  pathname: '/activities/add',
                }}
              >
                Add a workout
              </Link>
            </li>
            )}
            {props.user.isAdmin && (
            <li className="nav-item">
              <Link
                className="nav-link"
                to={{
                  pathname: '/admin',
                }}
              >
                Admin
              </Link>
            </li>
            )}
          </ul>
          <ul className="navbar-nav flex-row ml-md-auto d-none d-md-flex">
            {!props.user.isAuthenticated && (
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
            {!props.user.isAuthenticated && (
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
            {props.user.picture === true && (
            <img
              alt="Avatar"
              src={`${apiUrl}users/${props.user.id}/picture` +
                  `?${Date.now()}`}
              className="img-fluid App-nav-profile-img"
            />
            )}
            {props.user.isAuthenticated && (
            <li className="nav-item">
              <Link
                className="nav-link"
                to={{
                  pathname: '/profile',
                }}
              >
                {props.user.username}
              </Link>
            </li>
            )}
            {props.user.isAuthenticated && (
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
      </nav>
    </header>
  )
}
export default connect(
  state => ({
    user: state.user,
  })
)(NavBar)
