import React from 'react'
import { Helmet } from 'react-helmet'
import { withTranslation } from 'react-i18next'
import { connect } from 'react-redux'

import i18n from '../../i18n'
import Message from '../Common/Message'
import NoWorkouts from '../Common/NoWorkouts'
import WorkoutsFilter from './WorkoutsFilter'
import WorkoutsList from './WorkoutsList'
import { getOrUpdateData } from '../../actions'
import { getMoreWorkouts } from '../../actions/workouts'
import { convertBack } from '../../utils/conversions'

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
        if (i18n.t('km') === 'mi') {
          if (params.distance_from) {
            params.distance_from = `${convertBack(
              params.distance_from,
              'mi',
              'down'
            )}`
          }
          if (params.distance_to) {
            params.distance_to = `${convertBack(
              params.distance_to,
              'mi',
              'up'
            )}`
          }
          if (params.ave_speed_from) {
            params.ave_speed_from = `${convertBack(
              params.ave_speed_from,
              'mi',
              'down'
            )}`
          }
          if (params.ave_speed_to) {
            params.ave_speed_to = `${convertBack(
              params.ave_speed_to,
              'mi',
              'up'
            )}`
          }
          if (params.max_speed_from) {
            params.max_speed_from = `${convertBack(
              params.max_speed_from,
              'mi',
              'down'
            )}`
          }
          if (params.max_speed_to) {
            params.max_speed_to = `${convertBack(
              params.max_speed_to,
              'mi',
              'up'
            )}`
          }
        }
        dispatch(getOrUpdateData('getData', 'workouts', params))
      },
      loadMoreWorkouts: params => {
        dispatch(getMoreWorkouts(params))
      },
    })
  )(Workouts)
)
