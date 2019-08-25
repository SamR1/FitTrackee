import { format } from 'date-fns'
import React from 'react'
import { connect } from 'react-redux'
import {
   Area, ComposedChart, Line, ResponsiveContainer, Tooltip, XAxis, YAxis
} from 'recharts'

import {
  getActivityChartData, getSegmentChartData
} from '../../../actions/activities'


class ActivityCharts extends React.Component {
  constructor(props, context) {
    super(props, context)
    this.state = {
      displayDistance: true,
      dataToHide: []
    }
  }

  componentDidMount() {
    if (this.props.dataType === 'activity') {
      this.props.loadActivityData(this.props.activity.id)
    } else {
      this.props.loadSegmentData(this.props.activity.id, this.props.segmentId)
    }
  }

  componentDidUpdate(prevProps) {
    if (this.props.dataType === 'activity' && (
      prevProps.activity.id !== this.props.activity.id)
    ) {
        this.props.loadActivityData(this.props.activity.id)
    }
    if (this.props.dataType === 'segment' && (
      prevProps.segmentId !== this.props.segmentId)
    ) {
      this.props.loadSegmentData(this.props.activity.id, this.props.segmentId)
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

  handleLegendChange (e) {
    const { dataToHide } = this.state
    const name = e.target.name // eslint-disable-line prefer-destructuring
    if (dataToHide.find(d => d === name)) {
      dataToHide.splice(dataToHide.indexOf(name), 1)
    } else {
      dataToHide.push(name)
    }
    this.setState({ dataToHide })
  }

  displayData (name) {
    const { dataToHide } = this.state
    return !dataToHide.find(d => d === name)
  }

  render() {
    const { chartData, updateCoordinates } = this.props
    const { displayDistance } = this.state
    const xInterval = chartData ? parseInt(chartData.length / 10, 10) : 0
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
        {chartData && chartData.length > 0 ? (
          <div>
            <div className="row chart-radio">
              <label className="radioLabel col-md-1">
                <input
                  type="radio"
                  name="distance"
                  checked={displayDistance}
                  onChange={e => this.handleRadioChange(e)}
                />
                distance
              </label>
              <label className="radioLabel col-md-1">
                <input
                  type="radio"
                  name="duration"
                  checked={!displayDistance}
                  onChange={e => this.handleRadioChange(e)}
                />
                duration
              </label>
            </div>
            <div className="row chart-radio">
              <div className="col-md-5" />
              <label className="radioLabel col-md-1">
                <input
                  type="checkbox"
                  name="speed"
                  checked={this.displayData('speed')}
                  onChange={e => this.handleLegendChange(e)}
                />
                speed
              </label>
              <label className="radioLabel col-md-1">
                <input
                  type="checkbox"
                  name="elevation"
                  checked={this.displayData('elevation')}
                  onChange={e => this.handleLegendChange(e)}
                />
                elevation
              </label>
              <div className="col-md-5" />
            </div>
            <div className="row chart">
              <ResponsiveContainer height={300}>
                <ComposedChart
                  data={chartData}
                  margin={{ top: 15, right: 30, left: 20, bottom: 15 }}
                  onMouseMove={e => updateCoordinates(e.activePayload)}
                  onMouseLeave={() => updateCoordinates(null)}
                >
                  <XAxis
                    allowDecimals={false}
                    dataKey={xDataKey}
                    label={{ value: xDataKey, offset: 0, position: 'bottom' }}
                    scale={xScale}
                    interval={xInterval}
                    tickFormatter={value => displayDistance
                                            ? value
                                            : format(value, 'HH:mm:ss')}
                    type="number"
                  />
                  <YAxis
                    label={{
                      value: 'speed (km/h)', angle: -90, position: 'left'
                    }}
                    yAxisId="left"
                  />
                  <YAxis
                    label={{
                      value: 'altitude (m)', angle: -90, position: 'right'
                    }}
                    yAxisId="right" orientation="right"
                  />
                  {this.displayData('elevation') && (
                    <Area
                      yAxisId="right"
                      type="linear"
                      dataKey="elevation"
                      fill="#e5e5e5"
                      stroke="#cccccc"
                      dot={false}
                      unit=" m"
                    />
                  )}
                  {this.displayData('speed') && (
                    <Line
                      yAxisId="left"
                      type="linear"
                      dataKey="speed"
                      stroke="#8884d8"
                      strokeWidth={2}
                      dot={false}
                      unit=" km/h"
                    />
                  )}
                  <Tooltip
                    labelFormatter={value => displayDistance
                                    ? `distance: ${value} km`
                                    : `duration: ${format(value, 'HH:mm:ss')}`}
                  />
                </ComposedChart>
              </ResponsiveContainer>
            </div>
            <div className="chart-info">
              data from gpx, without any cleaning
            </div>
          </div>
        ) : (
          'No data to display'
        )}
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
    loadSegmentData: (activityId, segmentId) => {
      dispatch(getSegmentChartData(activityId, segmentId))
    },
  })
)(ActivityCharts)
