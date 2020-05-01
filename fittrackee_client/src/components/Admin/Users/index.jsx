import { format } from 'date-fns'
import React from 'react'
import { connect } from 'react-redux'
import { Helmet } from 'react-helmet'
import { Link } from 'react-router-dom'

import Message from '../../Common/Message'
import { history } from '../../../index'
import { getOrUpdateData } from '../../../actions'
import { apiUrl } from '../../../utils'

class AdminUsers extends React.Component {
  componentDidMount() {
    this.props.loadUsers()
  }

  render() {
    const { message, t, updateUser, authUser, users } = this.props
    return (
      <div>
        <Helmet>
          <title>FitTrackee - {t('administration:Administration')}</title>
        </Helmet>
        {message && <Message message={message} t={t} />}
        <div className="container">
          <div className="row">
            <div className="col card">
              <div className="card-body">
                <table className="table table-borderless">
                  <thead>
                    <tr>
                      <th>#</th>
                      <th>{t('user:Username')}</th>
                      <th>{t('user:Email')}</th>
                      <th>{t('user:Registration Date')}</th>
                      <th>{t('activities:Activities')}</th>
                      <th>{t('user:Admin')}</th>
                      <th>{t('administration:Actions')}</th>
                    </tr>
                  </thead>
                  <tbody>
                    {users.map(user => (
                      <tr key={user.username}>
                        <td>
                          {user.picture === true && (
                            <img
                              alt="Avatar"
                              src={`${apiUrl}users/${
                                user.username
                              }/picture?${Date.now()}`}
                              className="img-fluid App-nav-profile-img"
                            />
                          )}
                        </td>
                        <td>
                          <Link to={`/users/${user.username}`}>
                            {user.username}
                          </Link>
                        </td>
                        <td>{user.email}</td>
                        <td>
                          {format(
                            new Date(user.created_at),
                            'dd/MM/yyyy HH:mm'
                          )}
                        </td>
                        <td>{user.nb_activities}</td>
                        <td>
                          {user.admin ? (
                            <i
                              className="fa fa-check-square-o custom-fa"
                              aria-hidden="true"
                              data-toggle="tooltip"
                            />
                          ) : (
                            <i
                              className="fa fa-square-o custom-fa"
                              aria-hidden="true"
                              data-toggle="tooltip"
                            />
                          )}
                        </td>
                        <td>
                          <input
                            type="submit"
                            className={`btn btn-${
                              user.admin ? 'dark' : 'primary'
                            } btn-sm`}
                            disabled={user.username === authUser.username}
                            value={
                              user.admin
                                ? t('administration:Remove admin rights')
                                : t('administration:Add admin rights')
                            }
                            onClick={() =>
                              updateUser(user.username, !user.admin)
                            }
                          />
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
                <input
                  type="submit"
                  className="btn btn-secondary"
                  onClick={() => history.push('/admin/')}
                  value={t('common:Back')}
                />
              </div>
            </div>
          </div>
        </div>
      </div>
    )
  }
}

export default connect(
  state => ({
    message: state.message,
    authUser: state.user,
    users: state.users.data,
  }),
  dispatch => ({
    loadUsers: () => {
      dispatch(getOrUpdateData('getData', 'users'))
    },
    updateUser: (userName, isAdmin) => {
      const data = { username: userName, admin: isAdmin }
      dispatch(getOrUpdateData('updateData', 'users', data, false))
    },
  })
)(AdminUsers)
