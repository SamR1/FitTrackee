import React from 'react'
import { connect } from 'react-redux'
import { Route, Switch } from 'react-router-dom'

import './App.css'
import Admin from './Admin'
import Activity from './Activity'
import Activities from './Activities'
import Dashboard from './Dashboard'
import Footer from './Footer'
import Logout from './User/Logout'
import NavBar from './NavBar'
import NotFound from './Others/NotFound'
import Profile from './User/Profile'
import ProfileEdit from './User/ProfileEdit'
import Statistics from './Statistics'
import UserForm from './User/UserForm'
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
          <Route exact path="/logout" component={Logout} />
          <Route exact path="/profile/edit" component={ProfileEdit} />
          <Route exact path="/profile" component={Profile} />
          <Route exact path="/activities/history" component={Activities} />
          <Route exact path="/activities/statistics" component={Statistics} />
          <Route path="/activities" component={Activity} />
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
