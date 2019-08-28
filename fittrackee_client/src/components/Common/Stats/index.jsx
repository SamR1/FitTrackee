import { format } from 'date-fns'
import React from 'react'
import { connect } from 'react-redux'

import { getStats } from '../../../actions/stats'
import { formatStats } from '../../../utils/stats'
import StatsChart from './StatsChart'

class Statistics extends React.PureComponent {
  componentDidMount() {
    this.updateData()
  }

  componentDidUpdate(prevProps) {
    if (
      (this.props.user.id && this.props.user.id !== prevProps.user.id) ||
      this.props.statsParams !== prevProps.statsParams
    ) {
      this.updateData()
    }
  }

  updateData() {
    if (this.props.user.id) {
      this.props.loadActivities(this.props.user.id, this.props.statsParams)
    }
  }

  render() {
    const {
      displayedSports,
      sports,
      statistics,
      statsParams,
      displayEmpty,
    } = this.props
    if (!displayEmpty && Object.keys(statistics).length === 0) {
      return 'No workouts'
    }
    const stats = formatStats(statistics, sports, statsParams, displayedSports)
    return <StatsChart sports={sports} stats={stats} />
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
      const dateFormat = 'yyyy-MM-dd'
      const params = {
        from: format(data.start, dateFormat),
        to: format(data.end, dateFormat),
        time: data.duration,
      }
      dispatch(getStats(userId, data.type, params))
    },
  })
)(Statistics)
