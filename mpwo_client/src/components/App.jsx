import React from 'react'
import { Route, Switch } from 'react-router-dom'

import './App.css'
import Dashboard from './Dashboard'
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
        <Switch>
          <Route exact path="/" component={Dashboard} />
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
          <Route exact path="/logout" component={Logout} />
        </Switch>
     </div>
    )
  }
}
