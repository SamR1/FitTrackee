// eslint-disable-next-line max-len
// source: https://blog.flowandform.agency/create-a-custom-calendar-in-react-3df1bfd0b728
import {
  addDays,
  addMonths,
  endOfMonth,
  endOfWeek,
  format,
  isSameDay,
  isSameMonth,
  startOfMonth,
  startOfWeek,
  subMonths,
} from 'date-fns'
import React, { Fragment } from 'react'
import { connect } from 'react-redux'
import { Link } from 'react-router-dom'

import { getMonthActivities } from '../../actions/activities'
import { getDateWithTZ } from '../../utils'
import { recordsLabels } from '../../utils/activities'

const getStartAndEndMonth = date => {
  const monthStart = startOfMonth(date)
  const monthEnd = endOfMonth(date)
  return {
    start: startOfWeek(monthStart),
    end: endOfWeek(monthEnd),
  }
}

class Calendar extends React.Component {
  constructor(props, context) {
    super(props, context)
    const calendarDate = new Date()
    this.state = {
      currentMonth: calendarDate,
      startDate: getStartAndEndMonth(calendarDate).start,
      endDate: getStartAndEndMonth(calendarDate).end,
    }
  }

  componentDidMount() {
    this.props.loadMonthActivities(this.state.startDate, this.state.endDate)
  }

  renderHeader() {
    const dateFormat = 'MMM yyyy'
    return (
      <div className="header row flex-middle">
        <div className="col col-start" onClick={() => this.handlePrevMonth()}>
          <i className="fa fa-chevron-left" aria-hidden="true" />
        </div>
        <div className="col col-center">
          <span>{format(this.state.currentMonth, dateFormat)}</span>
        </div>
        <div className="col col-end" onClick={() => this.handleNextMonth()}>
          <i className="fa fa-chevron-right" aria-hidden="true" />
        </div>
      </div>
    )
  }

  renderDays() {
    const dateFormat = 'ddd'
    const days = []
    const { startDate } = this.state

    for (let i = 0; i < 7; i++) {
      days.push(
        <div className="col col-center" key={i}>
          {format(addDays(startDate, i), dateFormat)}
        </div>
      )
    }
    return <div className="days row">{days}</div>
  }

  filterActivities(day) {
    const { activities, user } = this.props
    if (activities) {
      return activities.filter(act =>
        isSameDay(getDateWithTZ(act.activity_date, user.timezone), day)
      )
    }
    return []
  }

  renderCells() {
    const { currentMonth, startDate, endDate } = this.state
    const { sports } = this.props

    const dateFormat = 'd'
    const rows = []

    let days = []
    let day = startDate
    let formattedDate = ''

    while (day <= endDate) {
      for (let i = 0; i < 7; i++) {
        formattedDate = format(day, dateFormat)
        const dayActivities = this.filterActivities(day)
        const isDisabled = isSameMonth(day, currentMonth) ? '' : 'disabled'
        days.push(
          <div className={`col cell img-${isDisabled}`} key={day}>
            <span className="number">{formattedDate}</span>
            {dayActivities.map(act => (
              <Link key={act.id} to={`/activities/${act.id}`}>
                <Fragment>
                  <img
                    alt="activity sport logo"
                    className={`activity-sport ${isDisabled}`}
                    src={sports
                      .filter(s => s.id === act.sport_id)
                      .map(s => s.img)}
                    title={act.title}
                  />
                  {act.records.length > 0 && (
                    <sup>
                      <i
                        className="fa fa-trophy custom-fa-small"
                        aria-hidden="true"
                        title={act.records.map(
                          rec =>
                            ` ${
                              recordsLabels.filter(
                                r => r.record_type === rec.record_type
                              )[0].label
                            }`
                        )}
                      />
                    </sup>
                  )}
                </Fragment>
              </Link>
            ))}
          </div>
        )
        day = addDays(day, 1)
      }
      rows.push(
        <div className="row" key={day}>
          {days}
        </div>
      )
      days = []
    }
    return <div className="body">{rows}</div>
  }

  updateStateDate(calendarDate) {
    const { start, end } = getStartAndEndMonth(calendarDate)
    this.setState({
      currentMonth: calendarDate,
      startDate: start,
      endDate: end,
    })
    this.props.loadMonthActivities(start, end)
  }

  handleNextMonth() {
    const calendarDate = addMonths(this.state.currentMonth, 1)
    this.updateStateDate(calendarDate)
  }

  handlePrevMonth() {
    const calendarDate = subMonths(this.state.currentMonth, 1)
    this.updateStateDate(calendarDate)
  }

  render() {
    return (
      <div className="card activity-card">
        <div className="calendar">
          {this.renderHeader()}
          {this.renderDays()}
          {this.renderCells()}
        </div>
      </div>
    )
  }
}

export default connect(
  state => ({
    activities: state.calendarActivities.data,
    sports: state.sports.data,
    user: state.user,
  }),
  dispatch => ({
    loadMonthActivities: (start, end) => {
      const dateFormat = 'yyyy-MM-dd'
      dispatch(
        getMonthActivities(format(start, dateFormat), format(end, dateFormat))
      )
    },
  })
)(Calendar)
