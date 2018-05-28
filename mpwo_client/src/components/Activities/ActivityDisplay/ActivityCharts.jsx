import { format } from 'date-fns'
import React from 'react'
import { connect } from 'react-redux'
import {
   Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis
} from 'recharts'

import { getActivityChartData } from '../../../actions/activities'


class ActivityCharts extends React.Component {
  constructor(props, context) {
    super(props, context)
    this.state = {
      displayDistance: true,
    }
  }

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

  handleRadioChange (changeEvent) {
    this.setState({
      displayDistance:
        changeEvent.target.name === 'distance'
          ? changeEvent.target.value
          : !changeEvent.target.value
    })
  }

  render() {
    const { chartData } = this.props
    const { displayDistance } = this.state
    let xDataKey, xScale
    if (displayDistance) {
      xDataKey = 'distance'
      xScale = 'linear'
    } else {
      xDataKey = 'duration'
      xScale = 'time'
    }
    return (
      <div className="container">
        <div className="row chart-radio">
          <label className="radioLabel col-md-1">
            <input
              type="radio"
              name="distance"
              checked={displayDistance}
              onChange={event => this.handleRadioChange(event)}
            />
            distance
          </label>
          <label className="radioLabel col-md-1">
            <input
              type="radio"
              name="duration"
              checked={!displayDistance}
              onChange={event => this.handleRadioChange(event)}
            />
            duration
          </label>
        </div>
        <div className="row chart">
          <ResponsiveContainer height={300}>
            <LineChart
              data={chartData}
              margin={{ top: 15, right: 30, left: 20, bottom: 15 }}
            >
              <XAxis
                allowDecimals={false}
                dataKey={xDataKey}
                label={{ value: xDataKey, offset: 0, position: 'bottom' }}
                scale={xScale}
                tickFormatter={value => displayDistance
                                        ? value
                                        : format(value, 'HH:mm:ss')}
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
                labelFormatter={value => displayDistance
                                ? `${value} km`
                                : format(value, 'HH:mm:ss')}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
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
