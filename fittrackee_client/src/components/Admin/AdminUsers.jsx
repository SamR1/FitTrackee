import { format } from 'date-fns'
import React from 'react'
import { connect } from 'react-redux'
import { Helmet } from 'react-helmet'
import { Link } from 'react-router-dom'

import Message from '../Common/Message'
import Pagination from '../Common/Pagination'
import { history } from '../../index'
import { getOrUpdateData } from '../../actions'
import {
  apiUrl,
  formatUrl,
  sortOrders,
  translateValues,
  userFilters,
} from '../../utils'

class AdminUsers extends React.Component {
  constructor(props, context) {
    super(props, context)
    this.state = {
      page: null,
      per_page: null,
      order_by: 'created_at',
      order: 'asc',
    }
  }

  componentDidMount() {
    this.initState()
    this.props.loadUsers(this.props.location.query)
  }

  componentDidUpdate(prevProps) {
    if (prevProps.location.query !== this.props.location.query) {
      this.props.loadUsers(this.props.location.query)
    }
  }

  initState() {
    const { query } = this.props.location
    this.setState({
      page: query.page,
      per_page: query.per_page,
      order_by: query.order_by ? query.order_by : 'created_at',
      order: query.order ? query.order : 'asc',
    })
  }

  updatePage(key, value) {
    const query = Object.assign({}, this.state)
    query[key] = value
    this.setState(query)
    const url = formatUrl(this.props.location.pathname, query)
    history.push(url)
  }

  render() {
    const {
      authUser,
      location,
      message,
      t,
      pagination,
      updateUser,
      users,
    } = this.props
    const translatedFilters = translateValues(t, userFilters)
    const translatedSortOrders = translateValues(t, sortOrders)
    return (
      <div>
        <Helmet>
          <title>FitTrackee - {t('administration:Administration')}</title>
        </Helmet>
        {message && <Message message={message} t={t} />}
        <div className="container">
          <div className="row">
            <div className="col">
              <div className="card">
                <div className="card-header">{t('administration:Users')}</div>
                <div className="card-body">
                  <div className="row user-filters">
                    <div className="col-lg-4 col-md-6 col-sm-12">
                      <label htmlFor="order_by">
                        {t('common:Sort by')}:{' '}
                        <select
                          id="order_by"
                          name="order_by"
                          value={this.state.order_by}
                          onChange={e =>
                            this.updatePage('order_by', e.target.value)
                          }
                        >
                          {translatedFilters.map(filter => (
                            <option key={filter.key} value={filter.key}>
                              {filter.label}
                            </option>
                          ))}
                        </select>{' '}
                      </label>
                    </div>
                    <div className="col-lg-4 col-md-6 col-sm-12">
                      <label htmlFor="sort">
                        {t('common:Sort')}:{' '}
                        <select
                          id="sort"
                          name="sort"
                          value={this.state.order}
                          onChange={e =>
                            this.updatePage('order', e.target.value)
                          }
                        >
                          {translatedSortOrders.map(sort => (
                            <option key={sort.key} value={sort.key}>
                              {sort.label}
                            </option>
                          ))}
                        </select>{' '}
                      </label>
                    </div>
                  </div>
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
                            {user.picture === true ? (
                              <img
                                alt="Avatar"
                                src={`${apiUrl}users/${
                                  user.username
                                }/picture?${Date.now()}`}
                                className="img-fluid App-nav-profile-img"
                              />
                            ) : (
                              <i
                                className="fa fa-user-circle-o fa-2x no-picture"
                                aria-hidden="true"
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
                  <Pagination
                    pagination={pagination}
                    pathname={location.pathname}
                    query={this.state}
                    t={t}
                  />
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
      </div>
    )
  }
}

export default connect(
  state => ({
    authUser: state.user,
    location: state.router.location,
    message: state.message,
    pagination: state.users.pagination,
    users: state.users.data,
  }),
  dispatch => ({
    loadUsers: query => {
      dispatch(getOrUpdateData('getData', 'users', query))
    },
    updateUser: (userName, isAdmin) => {
      const data = { username: userName, admin: isAdmin }
      dispatch(getOrUpdateData('updateData', 'users', data, false))
    },
  })
)(AdminUsers)
