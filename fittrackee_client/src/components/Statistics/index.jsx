import {
  endOfMonth,
  endOfWeek,
  endOfYear,
  startOfMonth,
  startOfYear,
  subMonths,
  subYears
} from 'date-fns'
import React from 'react'

import Stats from '../Common/Stats'

const durations = ['week', 'month', 'year']

export default class Statistics extends React.Component {
  constructor(props, context) {
    super(props, context)
    const date = new Date()
    this.state = {
      start: startOfMonth(subMonths(date, 11)),
      end: endOfMonth(date),
      duration: 'month',
      type: 'by_time',
    }
  }

  handleOnChange(e) {
    const duration = e.target.value
    const date = new Date()
    const start = duration === 'year'
      ? startOfYear(subYears(date, 9))
      : duration === 'week'
        ? startOfMonth(subMonths(date, 2))
        : startOfMonth(subMonths(date, 11))
    const end = duration === 'year'
      ? endOfYear(date)
      : duration === 'week'
        ? endOfWeek(date)
        : endOfMonth(date)
    this.setState({ duration, end, start })
  }

  render() {
    const { duration } = this.state
    return (
      <div className="container dashboard">
        <div className="card activity-card">
          <div className="card-header">
            Statistics
          </div>
          <div className="card-body">
            <div className="chart-filters row">
              <div className="col-md-3">
                <select
                  className="form-control input-lg"
                  name="duration"
                  defaultValue={duration}
                  onChange={e => this.handleOnChange(e)}
                >
                  {durations.map(d => (
                    <option key={d} value={d}>
                      {d}
                    </option>
                  ))}
                </select>
              </div>
            </div>
            <Stats statsParams={this.state} />
          </div>
        </div>
      </div>
    )
  }
}
