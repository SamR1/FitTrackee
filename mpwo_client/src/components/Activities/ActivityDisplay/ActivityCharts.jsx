import { format } from 'date-fns'
import React from 'react'
import { connect } from 'react-redux'
import {
   Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis
} from 'recharts'

import { getActivityChartData } from '../../../actions/activities'


class ActivityCharts extends React.Component {
  componentDidMount() {
    this.props.loadActivityData(this.props.activity.id)
  }

  componentDidUpdate(prevProps) {
    if (prevProps.activity.id !==
      this.props.activity.id) {
        this.props.loadActivityData(this.props.activity.id)
    }
  }

  componentWillUnmount() {
    this.props.loadActivityData(null)
  }

  render() {
    const { chartData } = this.props
    return (
      <div>
        <ResponsiveContainer height={300}>
          <LineChart
            data={chartData}
            margin={{ top: 15, right: 30, left: 20, bottom: 15 }}
          >
            <XAxis
              dataKey="duration"
              label={{ value: 'duration', offset: 0, position: 'bottom' }}
              scale="time"
              tickFormatter={time => format(time, 'HH:mm:ss')}
              type="number"
            />
            <YAxis
              label={{ value: 'speed (km/h)', angle: -90, position: 'left' }}
              yAxisId="left"
            />
            <YAxis
              label={{ value: 'altitude (m)', angle: -90, position: 'right' }}
              yAxisId="right" orientation="right"
            />
            <Line
              yAxisId="left"
              type="linear"
              dataKey="speed"
              stroke="#8884d8"
              dot={false}
            />
            <Line
              yAxisId="right"
              type="linear"
              dataKey="elevation"
              stroke="#808080"
              dot={false}
            />
            <Tooltip
              labelFormatter={time => format(time, 'HH:mm:ss')}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    )
  }
}

export default connect(
  state => ({
    chartData: state.chartData
  }),
  dispatch => ({
    loadActivityData: activityId => {
      dispatch(getActivityChartData(activityId))
    },
  })
)(ActivityCharts)
