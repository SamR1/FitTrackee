import React from 'react'
import { connect } from 'react-redux'
import { Route, Switch } from 'react-router-dom'

import { getOrUpdateData } from '../../../actions'
import AdminPage from '../generic/AdminPage'
import AdminSport from './AdminSport'
import AdminSportsAdd from './AdminSportsAdd'
import NotFound from '../../Others/NotFound'

class AdminSports extends React.Component {
  componentDidMount() {
    this.props.loadSports()
  }
  render() {
    const { sports } = this.props
    return (
      <Switch>
        <Route
          exact
          path="/admin/sports"
          render={() => <AdminPage data={sports} target="sports" />}
        />
        <Route exact path="/admin/sports/add" component={AdminSportsAdd} />
        <Route exact path="/admin/sports/:sportId" component={AdminSport} />
        <Route component={NotFound} />
      </Switch>
    )
  }
}

export default connect(
  state => ({
    sports: state.sports,
    user: state.user,
  }),
  dispatch => ({
    loadSports: () => {
      dispatch(getOrUpdateData('getData', 'sports'))
    },
  })
)(AdminSports)
