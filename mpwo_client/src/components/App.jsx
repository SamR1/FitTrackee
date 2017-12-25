import React from 'react'
import { Redirect, Route, Switch } from 'react-router-dom'

import './App.css'
import Dashboard from './Dashboard'
import Logout from './Logout'
import NavBar from './NavBar'
import UserForm from './User/UserForm'
import { isLoggedIn } from '../utils'

export default class App extends React.Component {

  constructor(props) {
    super(props)
    this.props = props
  }

  render() {
    return (
      <div className="App">
        <NavBar />
        <Switch>
          <Route
            exact path="/"
            render={() => (
              isLoggedIn() ? (
                <Dashboard />
              ) : (
                <Redirect to="/login" />
              )
            )}
          />
          <Route
            exact path="/register"
            render={() => (
              isLoggedIn() ? (
                <Redirect to="/" />
              ) : (
                <UserForm
                  formType={'Register'}
                />
              )
            )}
          />
          <Route
            exact path="/login"
            render={() => (
              isLoggedIn() ? (
                <Redirect to="/" />
              ) : (
                <UserForm
                  formType={'Login'}
                />
              )
            )}
          />
          <Route exact path="/logout" component={Logout} />
        </Switch>
     </div>
    )
  }
}
