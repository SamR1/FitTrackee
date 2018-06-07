import React from 'react'
import { Helmet } from 'react-helmet'
import { connect } from 'react-redux'
import { Redirect, Route, Switch } from 'react-router-dom'

import AdminMenu from './Sports/AdminMenu'
import AdminSport from './Sports/AdminSport'
import AdminSports from './Sports/AdminSports'
import AdminSportsAdd from './Sports/AdminSportsAdd'
import AccessDenied from './../Others/AccessDenied'
import NotFound from './../Others/NotFound'
import { isLoggedIn } from '../../utils'

function Admin (props) {
  const { user } = props
  return (
    <div>
      <Helmet>
        <title>mpwo - Admin</title>
      </Helmet>
      {isLoggedIn() ? (
        user.isAdmin ? (
          <Switch>
            <Route exact path="/admin" component={AdminMenu} />
            <Route exact path="/admin/sports" component={AdminSports} />
            <Route
              exact path="/admin/sports/add"
              component={AdminSportsAdd}
            />
            <Route
              exact path="/admin/sports/:sportId"
              component={AdminSport}
            />
            <Route component={NotFound} />
          </Switch>
        ) : (
          <AccessDenied />
        )
      ) : (<Redirect to="/login" />)}
    </div>
  )
}

export default connect(
  state => ({
    user: state.user,
  })
)(Admin)
