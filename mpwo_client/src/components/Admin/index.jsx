import React from 'react'
import { Helmet } from 'react-helmet'
import { connect } from 'react-redux'
import { Redirect, Route, Switch } from 'react-router-dom'

import AdminMenu from './AdminMenu'
import AdminSport from './AdminSport'
import AdminSports from './AdminSports'
import AccessDenied from './../Others/AccessDenied'
import NotFound from './../Others/NotFound'
import { isLoggedIn } from '../../utils'

class Admin extends React.Component {
  componentDidMount() {}
  render() {
    const { user } = this.props
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
              <Route path="/admin/sport" component={AdminSport} />
              <Route component={NotFound} />
            </Switch>
          ) : (
            <AccessDenied />
          )
        ) : (<Redirect to="/login" />)}
      </div>
    )
  }
}

export default connect(
  state => ({
    user: state.user,
  })
)(Admin)
