import React from 'react'
import {
  Bar,
  BarChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'

import { activityColors } from '../../../utils/activities'
import { formatValue } from '../../../utils/stats'
import CustomTooltip from './CustomTooltip'
import CustomLabel from './CustomLabel'

export default class StatsCharts extends React.PureComponent {
  constructor(props, context) {
    super(props, context)
    this.state = {
      displayedData: 'distance',
    }
  }
  handleRadioChange(changeEvent) {
    this.setState({
      displayedData: changeEvent.target.name,
    })
  }

  render() {
    const { displayedData } = this.state
    const { sports, stats, t } = this.props
    if (Object.keys(stats).length === 0) {
      return t('common:No workouts.')
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
            {t('statistics:distance')}
          </label>
          <label className="radioLabel col">
            <input
              type="radio"
              name="duration"
              checked={displayedData === 'duration'}
              onChange={e => this.handleRadioChange(e)}
            />
            {t('statistics:duration')}
          </label>
          <label className="radioLabel col">
            <input
              type="radio"
              name="activities"
              checked={displayedData === 'activities'}
              onChange={e => this.handleRadioChange(e)}
            />
            {t('statistics:activities')}
          </label>
        </div>
        <ResponsiveContainer height={300}>
          <BarChart data={stats[displayedData]} margin={{ top: 15, bottom: 0 }}>
            <XAxis
              dataKey="date"
              interval={0} // to force to display all ticks
            />
            <YAxis tickFormatter={value => formatValue(displayedData, value)} />
            <Tooltip
              content={<CustomTooltip displayedData={displayedData} />}
            />
            {sports.map((s, i) => (
              <Bar
                // disable for now due to problems  w/ CustomLabel
                // see https://github.com/recharts/recharts/issues/829
                isAnimationActive={false}
                key={s.id}
                dataKey={s.label}
                stackId="a"
                fill={activityColors[i]}
                label={
                  i === sports.length - 1 ? (
                    <CustomLabel displayedData={displayedData} />
                  ) : (
                    ''
                  )
                }
                name={t(`sports:${s.label}`)}
              />
            ))}
          </BarChart>
        </ResponsiveContainer>
      </div>
    )
  }
}
