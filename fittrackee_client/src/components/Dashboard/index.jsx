import React from 'react'
import { Helmet } from 'react-helmet'
import { withTranslation } from 'react-i18next'
import { connect } from 'react-redux'

import Calendar from './Calendar'
import Message from '../Common/Message'
import NoWorkouts from '../Common/NoWorkouts'
import Records from './Records'
import Statistics from './Statistics'
import UserStatistics from './UserStatistics'
import WorkoutCard from './WorkoutCard'
import { getOrUpdateData } from '../../actions'
import { getMoreWorkouts } from '../../actions/workouts'

class DashBoard extends React.Component {
  constructor(props, context) {
    super(props, context)
    this.state = {
      page: 1,
    }
  }

  componentDidMount() {
    this.props.loadWorkouts()
  }

  render() {
    const {
      loadMoreWorkouts,
      message,
      records,
      sports,
      t,
      user,
      workouts,
    } = this.props
    const paginationEnd =
      workouts.length > 0
        ? workouts[workouts.length - 1].previous_workout === null
        : true
    const { page } = this.state
    return (
      <div>
        <Helmet>
          <title>FitTrackee - {t('common:Dashboard')}</title>
        </Helmet>
        {message ? (
          <Message message={message} t={t} />
        ) : (
          workouts &&
          user.total_duration &&
          sports.length > 0 && (
            <div className="container dashboard">
              <UserStatistics user={user} t={t} />
              <div className="row">
                <div className="col-md-4">
                  <Statistics t={t} />
                  <Records
                    t={t}
                    records={records}
                    sports={sports}
                    user={user}
                  />
                </div>
                <div className="col-md-8">
                  <Calendar weekm={user.weekm} />
                  {workouts.length > 0 ? (
                    workouts.map(workout => (
                      <WorkoutCard
                        workout={workout}
                        key={workout.id}
                        sports={sports}
                        t={t}
                        user={user}
                      />
                    ))
                  ) : (
                    <NoWorkouts t={t} />
                  )}
                  {!paginationEnd && (
                    <input
                      type="submit"
                      className="btn btn-default btn-md btn-block"
                      value="Load more workouts"
                      onClick={() => {
                        loadMoreWorkouts(page + 1)
                        this.setState({ page: page + 1 })
                      }}
                    />
                  )}
                </div>
              </div>
            </div>
          )
        )}
      </div>
    )
  }
}

export default withTranslation()(
  connect(
    state => ({
      workouts: state.workouts.data,
      message: state.message,
      records: state.records.data,
      sports: state.sports.data,
      user: state.user,
    }),
    dispatch => ({
      loadWorkouts: () => {
        dispatch(getOrUpdateData('getData', 'workouts', { page: 1 }))
        dispatch(getOrUpdateData('getData', 'records'))
      },
      loadMoreWorkouts: page => {
        dispatch(getMoreWorkouts({ page }))
      },
    })
  )(DashBoard)
)
