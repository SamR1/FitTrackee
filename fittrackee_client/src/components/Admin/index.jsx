import React from 'react'
import { Helmet } from 'react-helmet'
import { connect } from 'react-redux'
import { Link, Redirect, Route, Switch } from 'react-router-dom'

import AdminDashboard from './AdminDashboard'
import AdminMenu from './AdminMenu'
import AdminSports from './Sports/AdminSports'
import AccessDenied from './../Others/AccessDenied'
import NotFound from './../Others/NotFound'
import { isLoggedIn } from '../../utils'

function Admin(props) {
  const { user } = props
  return (
    <div>
      <Helmet>
        <title>FitTrackee - Admin</title>
      </Helmet>
      <div className="container dashboard">
        <div className="row">
          <div className="col-md-3">
            <div className="card activity-card">
              <div className="card-header">
                <Link
                  to={{
                    pathname: '/admin/',
                  }}
                >
                  Administration
                </Link>
              </div>
              <div className="card-body">
                <AdminMenu />
              </div>
            </div>
          </div>
          <div className="col-md-9">
            {isLoggedIn() ? (
              user.admin ? (
                <Switch>
                  <Route exact path="/admin" component={AdminDashboard} />
                  <Route path="/admin/sports" component={AdminSports} />
                  <Route component={NotFound} />
                </Switch>
              ) : (
                <AccessDenied />
              )
            ) : (
              <Redirect to="/login" />
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default connect(state => ({
  user: state.user,
}))(Admin)
