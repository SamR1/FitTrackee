import { format } from 'date-fns'
import React from 'react'
import { connect } from 'react-redux'
import { Helmet } from 'react-helmet'
import { Link } from 'react-router-dom'

import Message from '../../Common/Message'
import { history } from '../../../index'
import { getOrUpdateData } from '../../../actions'

class AdminUsers extends React.Component {
  componentDidMount() {
    this.props.loadUsers()
  }

  render() {
    const { message, t, users } = this.props
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
                <table className="table">
                  <thead>
                    <tr>
                      <th>{t('administration:id')}</th>
                      <th>{t('user:Username')}</th>
                      <th>{t('user:Email')}</th>
                      <th>{t('user:Registration Date')}</th>
                      <th>{t('activities:Activities')}</th>
                      <th>{t('user:Admin')}</th>
                    </tr>
                  </thead>
                  <tbody>
                    {users.map(user => (
                      <tr key={user.id}>
                        <th scope="row">{user.id}</th>
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
                      </tr>
                    ))}
                  </tbody>
                </table>
                <input
                  type="submit"
                  className="btn btn-secondary btn-lg btn-block"
                  onClick={() => history.push('/admin/')}
                  value={t('administration:Back')}
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
    users: state.users.data,
  }),
  dispatch => ({
    loadUsers: () => {
      dispatch(getOrUpdateData('getData', 'users'))
    },
  })
)(AdminUsers)
