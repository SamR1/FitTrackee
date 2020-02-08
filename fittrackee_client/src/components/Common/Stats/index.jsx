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
      (this.props.user.username &&
        this.props.user.username !== prevProps.user.username) ||
      this.props.statsParams !== prevProps.statsParams
    ) {
      this.updateData()
    }
  }

  updateData() {
    if (this.props.user.username) {
      this.props.loadActivities(
        this.props.user.username,
        this.props.user.weekm,
        this.props.statsParams
      )
    }
  }

  render() {
    const {
      displayedSports,
      sports,
      statistics,
      statsParams,
      displayEmpty,
      t,
      user,
    } = this.props
    if (!displayEmpty && Object.keys(statistics).length === 0) {
      return <span>{t('common:No workouts.')}</span>
    }
    const stats = formatStats(
      statistics,
      sports,
      statsParams,
      displayedSports,
      user.weekm
    )
    return <StatsChart sports={sports} stats={stats} t={t} />
  }
}

export default connect(
  state => ({
    sports: state.sports.data,
    statistics: state.statistics.data,
    user: state.user,
  }),
  dispatch => ({
    loadActivities: (userName, weekm, data) => {
      const dateFormat = 'yyyy-MM-dd'
      // depends on user config (first day of week)
      const time =
        data.duration === 'week'
          ? `${data.duration}${weekm ? 'm' : ''}`
          : data.duration
      const params = {
        from: format(data.start, dateFormat),
        to: format(data.end, dateFormat),
        time: time,
      }
      dispatch(getStats(userName, data.type, params))
    },
  })
)(Statistics)
