import React from 'react'
import { Route, Switch } from 'react-router-dom'

import './App.css'
import Logout from './Logout'
import NavBar from './NavBar'
import UserForm from './User/UserForm'

export default class App extends React.Component {
  constructor(props) {
    super(props)
    this.props = props
  }

  render() {
    return (
      <div className="App">
        <NavBar />
        <div className="container">
          <div className="row">
            <div className="col-md-6">
              <br />
              <Switch>
                <Route
                  exact path="/register"
                  render={() => (
                    <UserForm
                      formType={'Register'}
                    />
                  )}
                />
                <Route
                  exact path="/login"
                  render={() => (
                    <UserForm
                      formType={'Login'}
                    />
                  )}
                />
                <Route
                  exact path="/logout"
                  render={() => (
                    <Logout />
                  )}
                />
              </Switch>
            </div>
          </div>
        </div>
      </div>
    )
  }
}
