import React from 'react'
import { connect } from 'react-redux'
import { Redirect, Route, Switch } from 'react-router-dom'

import NotFound from './../Others/NotFound'
import WorkoutAdd from './WorkoutAdd'
import WorkoutDisplay from './WorkoutDisplay'
import WorkoutEdit from './WorkoutEdit'
import { isLoggedIn } from '../../utils'

function Workout() {
  return (
    <div>
      {isLoggedIn() ? (
        <Switch>
          <Route exact path="/workouts/add" component={WorkoutAdd} />
          <Route exact path="/workouts/:workoutId" component={WorkoutDisplay} />
          <Route
            exact
            path="/workouts/:workoutId/edit"
            component={WorkoutEdit}
          />
          <Route
            path="/workouts/:workoutId/segment/:segmentId"
            component={WorkoutDisplay}
          />
          <Route component={NotFound} />
        </Switch>
      ) : (
        <Redirect to="/login" />
      )}
    </div>
  )
}

export default connect(state => ({
  user: state.user,
}))(Workout)
