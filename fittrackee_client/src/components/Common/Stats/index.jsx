import { format } from 'date-fns'
import React from 'react'
import { connect } from 'react-redux'

import { getStats } from '../../../actions/stats'
import { formatStats } from '../../../utils/stats'
import StatsChart from './StatsChart'


class Statistics extends React.PureComponent {
  componentDidMount() {
    this.props.loadActivities(
      this.props.user.id,
      this.props.statsParams,
    )
  }

  componentDidUpdate(prevProps) {
    if (this.props.statsParams !== prevProps.statsParams) {
      this.props.loadActivities(
        this.props.user.id,
        this.props.statsParams,
      )
    }
  }

  render() {
    const { displayedSports, sports, statistics, statsParams } = this.props
    const stats = formatStats(statistics, sports, statsParams, displayedSports)
    return (
      <>
        {Object.keys(statistics).length === 0 ? (
          'No workouts'
        ) : (
          <StatsChart
            sports={sports}
            stats={stats}
          />
          )}
      </>
    )
  }
}

export default connect(
  state => ({
    sports: state.sports.data,
    statistics: state.statistics.data,
    user: state.user,
  }),
  dispatch => ({
    loadActivities: (userId, data) => {
      const dateFormat = 'YYYY-MM-DD'
      const params = {
        from: format(data.start, dateFormat),
        to: format(data.end, dateFormat),
        time: data.duration
      }
      dispatch(getStats(userId, data.type, params))
    },
  })
)(Statistics)
