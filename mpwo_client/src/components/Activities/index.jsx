import React from 'react'
import { Helmet } from 'react-helmet'
import { connect } from 'react-redux'
import { Redirect, Route, Switch } from 'react-router-dom'

import ActivityAdd from './ActivityAdd'
import ActivityDisplay from './ActivityDisplay'
import NotFound from './../Others/NotFound'
import { isLoggedIn } from '../../utils'

class Activity extends React.Component {
  componentDidMount() {}
  render() {
    return (
      <div>
        <Helmet>
          <title>mpwo - Admin</title>
        </Helmet>
        {isLoggedIn() ? (
          <Switch>
            <Route exact path="/activities/add" component={ActivityAdd} />
            <Route path="/activities" component={ActivityDisplay} />
            <Route component={NotFound} />
          </Switch>
        ) : (<Redirect to="/login" />)}
      </div>
    )
  }
}

export default connect(
  state => ({
    user: state.user,
  })
)(Activity)
