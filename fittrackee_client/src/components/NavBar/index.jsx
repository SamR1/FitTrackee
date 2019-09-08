import React from 'react'
import { Translation } from 'react-i18next'
import { connect } from 'react-redux'
import { Link } from 'react-router-dom'

import { apiUrl } from '../../utils'

class NavBar extends React.PureComponent {
  render() {
    const { id, isAuthenticated, picture, username } = this.props
    return (
      <Translation>
        {t => (
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
                            pathname: '/activities/history',
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
                            pathname: '/activities/statistics',
                          }}
                        >
                          {t('common:Statistics')}
                        </Link>
                      </li>
                    )}
                    {isAuthenticated && (
                      <li className="nav-item">
                        <Link
                          className="nav-link"
                          to={{
                            pathname: '/activities/add',
                          }}
                        >
                          <strong>{t('common:Add workout')}</strong>
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
                          {t('common:Register')}
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
                          {t('common:Login')}
                        </Link>
                      </li>
                    )}
                    {picture === true && (
                      <img
                        alt="Avatar"
                        src={`${apiUrl}users/${id}/picture?${Date.now()}`}
                        className="img-fluid App-nav-profile-img"
                      />
                    )}
                    {isAuthenticated && (
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
                    )}
                    {isAuthenticated && (
                      <li className="nav-item">
                        <Link
                          className="nav-link"
                          to={{
                            pathname: '/logout',
                          }}
                        >
                          {t('common:Logout')}
                        </Link>
                      </li>
                    )}
                  </ul>
                </div>
              </div>
            </nav>
          </header>
        )}
      </Translation>
    )
  }
}

export default connect(({ user }) => ({
  id: user.id,
  isAuthenticated: user.isAuthenticated,
  picture: user.picture,
  username: user.username,
}))(NavBar)
