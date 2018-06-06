import { endOfMonth, format, startOfMonth } from 'date-fns'
import React from 'react'
import { connect } from 'react-redux'
import {
   Bar, BarChart, ResponsiveContainer, Tooltip, XAxis, YAxis
} from 'recharts'

import { getStats } from '../../actions/stats'
import { formatStats } from '../../utils'


class Statistics extends React.Component {
  constructor(props, context) {
    super(props, context)
    const date = new Date()
    this.state = {
      start: startOfMonth(date),
      end: endOfMonth(date),
      displayedData: 'distance'
    }
  }

  componentDidMount() {
    this.props.loadMonthActivities(
      this.props.user.id,
      this.state.start,
      this.state.end,
    )
  }

  handleRadioChange (changeEvent) {
    this.setState({
      displayedData: changeEvent.target.name
    })
  }


  render() {
    const { sports, statistics } = this.props
    const { displayedData, end, start } = this.state
    const data = []
    const stats = formatStats(statistics, sports, start, end)
    const colors = [
      '#55a8a3',
      '#98C3A9',
      '#D0838A',
      '#ECC77E',
      '#926692',
      '#929292'
    ]
    return (
      <div className="card activity-card">
        <div className="card-header">
          This month
        </div>
        <div className="card-body chart-month">
          {data === [] ? (
            'No activities'
          ) : (
            <div>
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
                >
                  <XAxis dataKey="date" />
                  <YAxis />
                  <Tooltip />
                  {sports.map((s, i) => (
                    <Bar
                      key={s.id}
                      dataKey={s.label}
                      stackId="a"
                      fill={colors[i]}
                    />
                  ))}
                </BarChart>
              </ResponsiveContainer>
            </div>
            )}
        </div>
      </div>
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
    loadMonthActivities: (userId, start, end) => {
      const dateFormat = 'YYYY-MM-DD'
      const params = {
        start: format(start, dateFormat),
        end: format(end, dateFormat),
        time: 'week'
      }
      dispatch(getStats(userId, 'by_time', params))
    },
  })
)(Statistics)
