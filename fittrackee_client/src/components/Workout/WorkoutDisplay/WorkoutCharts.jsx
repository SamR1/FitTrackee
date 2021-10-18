import { format } from 'date-fns'
import React from 'react'
import { connect } from 'react-redux'
import {
  Area,
  ComposedChart,
  Line,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'

import {
  getSegmentChartData,
  getWorkoutChartData,
} from '../../../actions/workouts'

class WorkoutCharts extends React.Component {
  constructor(props, context) {
    super(props, context)
    this.state = {
      displayDistance: true,
      dataToHide: [],
    }
  }

  componentDidMount() {
    if (this.props.dataType === 'workout') {
      this.props.loadWorkoutData(this.props.workout.id)
    } else {
      this.props.loadSegmentData(this.props.workout.id, this.props.segmentId)
    }
  }

  componentDidUpdate(prevProps) {
    if (
      (this.props.dataType === 'workout' &&
        prevProps.workout.id !== this.props.workout.id) ||
      (this.props.dataType === 'workout' && prevProps.dataType === 'segment')
    ) {
      this.props.loadWorkoutData(this.props.workout.id)
    }
    if (
      this.props.dataType === 'segment' &&
      prevProps.segmentId !== this.props.segmentId
    ) {
      this.props.loadSegmentData(this.props.workout.id, this.props.segmentId)
    }
  }

  componentWillUnmount() {
    this.props.loadWorkoutData(null)
  }

  handleRadioChange(changeEvent) {
    this.setState({
      displayDistance:
        changeEvent.target.name === 'distance'
          ? changeEvent.target.value
          : !changeEvent.target.value,
    })
  }

  handleLegendChange(e) {
    const { dataToHide } = this.state
    const name = e.target.name // eslint-disable-line prefer-destructuring
    if (dataToHide.find(d => d === name)) {
      dataToHide.splice(dataToHide.indexOf(name), 1)
    } else {
      dataToHide.push(name)
    }
    this.setState({ dataToHide })
  }

  displayData(name) {
    const { dataToHide } = this.state
    return !dataToHide.find(d => d === name)
  }

  render() {
    const { chartData, t, updateCoordinates } = this.props
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
                {t('workouts:distance')}
              </label>
              <label className="radioLabel col-md-1">
                <input
                  type="radio"
                  name="duration"
                  checked={!displayDistance}
                  onChange={e => this.handleRadioChange(e)}
                />
                {t('workouts:duration')}
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
                {t('workouts:speed')}
              </label>
              <label className="radioLabel col-md-1">
                <input
                  type="checkbox"
                  name="elevation"
                  checked={this.displayData('elevation')}
                  onChange={e => this.handleLegendChange(e)}
                />
                {t('workouts:elevation')}
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
                    label={{
                      value: t(`workouts:${xDataKey}`),
                      offset: 0,
                      position: 'bottom',
                    }}
                    scale={xScale}
                    interval={xInterval}
                    tickFormatter={value =>
                      displayDistance ? value : format(value, 'HH:mm:ss')
                    }
                    type="number"
                  />
                  <YAxis
                    label={{
                      value: `${t('workouts:speed')} (${t('common:km')}/h)`,
                      angle: -90,
                      position: 'left',
                    }}
                    yAxisId="left"
                  />
                  <YAxis
                    label={{
                      value: `${t('workouts:elevation')} (${t('common:m')})`,
                      angle: -90,
                      position: 'right',
                    }}
                    yAxisId="right"
                    orientation="right"
                  />
                  {this.displayData('elevation') && (
                    <Area
                      yAxisId="right"
                      type="linear"
                      dataKey="elevation"
                      name={t('workouts:elevation')}
                      fill="#e5e5e5"
                      stroke="#cccccc"
                      dot={false}
                      unit={' ' + t('common:m')}
                    />
                  )}
                  {this.displayData('speed') && (
                    <Line
                      yAxisId="left"
                      type="linear"
                      dataKey="speed"
                      name={t('workouts:speed')}
                      stroke="#8884d8"
                      strokeWidth={2}
                      dot={false}
                      unit={' ' + t('common:km') + '/hr'}
                    />
                  )}
                  <Tooltip
                    labelFormatter={value =>
                      displayDistance
                        ? `${t('workouts:distance')}: ${value}
                            ${t('common:km')}`
                        : `${t('workouts:duration')}: ${format(
                            value,
                            'HH:mm:ss'
                          )}`
                    }
                  />
                </ComposedChart>
              </ResponsiveContainer>
            </div>
            <div className="chart-info">
              {t('workouts:data from gpx, without any cleaning')}
            </div>
          </div>
        ) : (
          t('workouts:No data to display')
        )}
      </div>
    )
  }
}

export default connect(
  state => ({
    chartData: state.chartData,
  }),
  dispatch => ({
    loadWorkoutData: workoutId => {
      dispatch(getWorkoutChartData(workoutId))
    },
    loadSegmentData: (workoutId, segmentId) => {
      dispatch(getSegmentChartData(workoutId, segmentId))
    },
  })
)(WorkoutCharts)
