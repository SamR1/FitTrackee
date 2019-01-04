import React from 'react'
import {
   Bar, BarChart, ResponsiveContainer, Tooltip, XAxis, YAxis
} from 'recharts'

import { activityColors } from '../../../utils/activities'
import { formatDuration } from '../../../utils/stats'
import CustomTooltip from './CustomTooltip'


export default class StatsCharts extends React.PureComponent {
  constructor(props, context) {
    super(props, context)
    this.state = {
      displayedData: 'distance'
    }
  }
  handleRadioChange (changeEvent) {
    this.setState({
      displayedData: changeEvent.target.name
    })
  }

  render() {
    const { displayedData } = this.state
    const { sports, stats } = this.props
    if (Object.keys(stats).length === 0) {
      return 'No workouts'
    }
    return (
      <div className="chart-stats">
        <div className="row chart-radio">
          <label className="radioLabel col">
            <input
              type="radio"
              name="distance"
              checked={displayedData === 'distance'}
              onChange={e => this.handleRadioChange(e)}
            />
            distance
          </label>
          <label className="radioLabel col">
            <input
              type="radio"
              name="duration"
              checked={displayedData === 'duration'}
              onChange={e => this.handleRadioChange(e)}
            />
            duration
          </label>
          <label className="radioLabel col">
            <input
              type="radio"
              name="activities"
              checked={displayedData === 'activities'}
              onChange={e => this.handleRadioChange(e)}
            />
            activities
          </label>
        </div>
        <ResponsiveContainer height={300}>
          <BarChart
            data={stats[displayedData]}
            margin={{ top: 15, bottom: 0 }}
          >
            <XAxis
              dataKey="date"
              interval={0} // to force to display all ticks
            />
            <YAxis
              tickFormatter={value => displayedData === 'distance'
                ? `${value} km`
                : displayedData === 'duration'
                  ? formatDuration(value)
                  : value
              }
            />
            <Tooltip content={
              <CustomTooltip
                displayedData={displayedData}
              />
            }
            />
            {sports.map((s, i) => (
              <Bar
                key={s.id}
                dataKey={s.label}
                stackId="a"
                fill={activityColors[i]}
                unit={displayedData === 'distance' ? ' km' : ''}
              />
            ))}
          </BarChart>
        </ResponsiveContainer>
      </div>
    )
  }
}
