import React from 'react'
import { connect } from 'react-redux'
import { Route, Switch } from 'react-router-dom'

import './App.css'
import Admin from './Admin'
import Workout from './Workout'
import Workouts from './Workouts'
import CurrentUserProfile from './User/CurrentUserProfile'
import Dashboard from './Dashboard'
import Footer from './Footer'
import Logout from './User/Logout'
import NavBar from './NavBar'
import NotFound from './Others/NotFound'
import PasswordReset from './User/PasswordReset'
import ProfileEdit from './User/ProfileEdit'
import Statistics from './Statistics'
import UserForm from './User/UserForm'
import UserProfile from './User/UserProfile'
import { getAppData } from '../actions/application'

class App extends React.Component {
  constructor(props) {
    super(props)
    this.props = props
  }
  componentDidMount() {
    this.props.loadAppConfig()
  }

  render() {
    return (
      <div className="App">
        <NavBar />
        <Switch>
          <Route exact path="/" component={Dashboard} />
          <Route
            exact
            path="/register"
            render={() => <UserForm formType={'register'} />}
          />
          <Route
            exact
            path="/login"
            render={() => <UserForm formType={'login'} />}
          />
          <Route
            exact
            path="/password-reset"
            render={() => <UserForm formType={'password reset'} />}
          />
          <Route
            exact
            path="/password-reset/request"
            render={() => <UserForm formType={'reset your password'} />}
          />
          <Route
            exact
            path="/password-reset/sent"
            render={() => <PasswordReset action={'sent'} />}
          />
          <Route
            exact
            path="/updated-password"
            render={() => <PasswordReset action={'updated'} />}
          />
          <Route exact path="/password-reset/sent" component={PasswordReset} />
          <Route exact path="/logout" component={Logout} />
          <Route exact path="/profile/edit" component={ProfileEdit} />
          <Route exact path="/profile" component={CurrentUserProfile} />
          <Route exact path="/workouts/history" component={Workouts} />
          <Route exact path="/workouts/statistics" component={Statistics} />
          <Route exact path="/users/:userName" component={UserProfile} />
          <Route path="/workouts" component={Workout} />
          <Route path="/admin" component={Admin} />
          <Route component={NotFound} />
        </Switch>
        <Footer />
      </div>
    )
  }
}
export default connect(
  () => ({}),
  dispatch => ({
    loadAppConfig: () => {
      dispatch(getAppData('config'))
    },
  })
)(App)
