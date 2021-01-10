import React from 'react'
import { Helmet } from 'react-helmet'
import { withTranslation } from 'react-i18next'
import { connect } from 'react-redux'

import Message from '../Common/Message'
import NoWorkouts from '../Common/NoWorkouts'
import WorkoutsFilter from './WorkoutsFilter'
import WorkoutsList from './WorkoutsList'
import { getOrUpdateData } from '../../actions'
import { getMoreWorkouts } from '../../actions/workouts'

class Workouts extends React.Component {
  constructor(props, context) {
    super(props, context)
    this.state = {
      params: {
        page: 1,
        per_page: 10,
      },
    }
  }

  componentDidMount() {
    this.props.loadWorkouts(this.state.params)
  }

  setParams(e) {
    const { params } = this.state
    if (e.target.value === '') {
      delete params[e.target.name]
    } else {
      params[e.target.name] = e.target.value
    }
    params.page = 1
    this.setState(params)
  }
  render() {
    const {
      loading,
      loadWorkouts,
      loadMoreWorkouts,
      message,
      sports,
      t,
      user,
      workouts,
    } = this.props
    const { params } = this.state
    const paginationEnd =
      workouts.length > 0
        ? workouts[workouts.length - 1].previous_workout === null
        : true
    return (
      <div>
        <Helmet>
          <title>FitTrackee - {t('common:Workouts')}</title>
        </Helmet>
        {message ? (
          <Message message={message} t={t} />
        ) : (
          <div className="container history">
            <div className="row">
              <div className="col-md-3">
                <WorkoutsFilter
                  sports={sports}
                  loadWorkouts={() => loadWorkouts(params)}
                  t={t}
                  updateParams={e => this.setParams(e)}
                />
              </div>
              <div className="col-md-9 workouts-result">
                <WorkoutsList
                  workouts={workouts}
                  loading={loading}
                  sports={sports}
                  t={t}
                  user={user}
                />
                {!paginationEnd && (
                  <input
                    type="submit"
                    className="btn btn-default btn-md btn-block"
                    value="Load more workouts"
                    onClick={() => {
                      params.page += 1
                      loadMoreWorkouts(params)
                      this.setState(params)
                    }}
                  />
                )}
                {workouts.length === 0 && <NoWorkouts t={t} />}
              </div>
            </div>
          </div>
        )}
      </div>
    )
  }
}

export default withTranslation()(
  connect(
    state => ({
      workouts: state.workouts.data,
      loading: state.loading,
      message: state.message,
      sports: state.sports.data,
      user: state.user,
    }),
    dispatch => ({
      loadWorkouts: params => {
        dispatch(getOrUpdateData('getData', 'workouts', params))
      },
      loadMoreWorkouts: params => {
        dispatch(getMoreWorkouts(params))
      },
    })
  )(Workouts)
)
