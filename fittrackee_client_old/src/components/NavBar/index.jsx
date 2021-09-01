import React from 'react'
import { connect } from 'react-redux'
import { withTranslation } from 'react-i18next'
import { Link } from 'react-router-dom'

import LanguageDropdown from './LanguageDropdown'
import { apiUrl } from '../../utils'

class NavBar extends React.PureComponent {
  render() {
    const { admin, isAuthenticated, picture, t, username } = this.props
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
                    {t('common:Dashboard')}
                  </Link>
                </li>
                {isAuthenticated && (
                  <li className="nav-item">
                    <Link
                      className="nav-link"
                      to={{
                        pathname: '/workouts/history',
                      }}
                    >
                      {t('Workouts')}
                    </Link>
                  </li>
                )}
                {isAuthenticated && (
                  <li className="nav-item">
                    <Link
                      className="nav-link"
                      to={{
                        pathname: '/workouts/statistics',
                      }}
                    >
                      {t('common:Statistics')}
                    </Link>
                  </li>
                )}
                {admin && (
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
                {isAuthenticated && (
                  <li className="nav-item">
                    <Link
                      className="nav-link"
                      to={{
                        pathname: '/workouts/add',
                      }}
                    >
                      <strong>{t('common:Add workout')}</strong>
                    </Link>
                  </li>
                )}
              </ul>
              {/* prettier-ignore */}
              <ul
                className="navbar-nav flex-row ml-md-auto d-none d-md-flex"
              >
                {!isAuthenticated && (
                  <li className="nav-item">
                    <Link
                      className="nav-link"
                      to={{
                        pathname: '/register',
                      }}
                    >
                      {t('user:Register')}
                    </Link>
                  </li>
                )}
                {!isAuthenticated && (
                  <li className="nav-item">
                    <Link
                      className="nav-link"
                      to={{
                        pathname: '/login',
                      }}
                    >
                      {t('user:Login')}
                    </Link>
                  </li>
                )}
                {isAuthenticated && (
                <>
                  {picture === true ? (
                    <img
                      alt="Avatar"
                      src={`${apiUrl}users/${username}/picture?${Date.now()}`}
                      className="img-fluid App-nav-profile-img"
                    />
                  ) : (
                    <i
                      className="fa fa-user-circle-o fa-2x no-picture"
                      aria-hidden="true"
                    />
                  )}
                  <li className="nav-item">
                    <Link
                      className="nav-link"
                      to={{
                        pathname: '/profile',
                      }}
                    >
                      {username}
                    </Link>
                  </li>
                  <li className="nav-item">
                    <Link
                      className="nav-link"
                      to={{
                        pathname: '/logout',
                      }}
                    >
                      {t('user:Logout')}
                    </Link>
                  </li>
                </>
                )}
                <li><LanguageDropdown /></li>
              </ul>
            </div>
          </div>
        </nav>
      </header>
    )
  }
}

export default withTranslation()(
  connect(({ user }) => ({
    admin: user.admin,
    isAuthenticated: user.isAuthenticated,
    picture: user.picture,
    username: user.username,
  }))(NavBar)
)
