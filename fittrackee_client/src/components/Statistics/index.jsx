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
import { connect } from 'react-redux'

import { activityColors } from '../../utils/activities'
import Stats from '../Common/Stats'

const durations = ['week', 'month', 'year']

class Statistics extends React.Component {
  constructor(props, context) {
    super(props, context)
    const date = new Date()
    this.state = {
      displayedSports: props.sports.map(sport => sport.id),
      statsParams: {
        start: startOfMonth(subMonths(date, 11)),
        end: endOfMonth(date),
        duration: 'month',
        type: 'by_time',
      }
    }
  }

  handleOnChangeDuration(e) {
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
    this.setState({ statsParams:
      { duration, end, start, type: 'by_time' }
    })
  }

  handleOnChangeSports(sportId) {
    const { displayedSports } = this.state
    if (displayedSports.includes(sportId)) {
      this.setState({
        displayedSports: displayedSports.filter(s => s !== sportId)
      })
    } else {
      this.setState({ displayedSports: displayedSports.concat([sportId]) })
    }
  }

  render() {
    const { displayedSports, statsParams } = this.state
    const { sports } = this.props
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
                  defaultValue={statsParams.duration}
                  onChange={e => this.handleOnChangeDuration(e)}
                >
                  {durations.map(d => (
                    <option key={d} value={d}>
                      {d}
                    </option>
                  ))}
                </select>
              </div>
            </div>
            <Stats
              displayedSports={displayedSports}
              statsParams={statsParams}
            />
            <div className="row chart-activities">
              {sports.map(sport => (
                <label className="col activity-label" key={sport.id}>
                  <input
                    type="checkbox"
                    checked={displayedSports.includes(sport.id)}
                    name={sport.label}
                    onChange={() => this.handleOnChangeSports(sport.id)}
                  />
                  <span style={{ color: activityColors[sport.id - 1] }}>
                    {` ${sport.label}`}
                  </span>
                </label>
              ))}
            </div>
          </div>
        </div>
      </div>
    )
  }
}

export default connect(
  state => ({
    sports: state.sports.data,
  })
)(Statistics)
