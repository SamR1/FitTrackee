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
  isToday,
  startOfMonth,
  startOfWeek,
  subMonths,
} from 'date-fns'
import { enUS, enGB, fr } from 'date-fns/locale'
import React from 'react'
import { connect } from 'react-redux'

import CalendarWorkouts from './CalendarWorkouts'
import { getMonthWorkouts } from '../../actions/workouts'
import { getDateWithTZ } from '../../utils'

const getStartAndEndMonth = (date, weekStartOnMonday) => {
  const monthStart = startOfMonth(date)
  const monthEnd = endOfMonth(date)
  const weekStartsOn = weekStartOnMonday ? 1 : 0
  return {
    start: startOfWeek(monthStart, { weekStartsOn }),
    end: endOfWeek(monthEnd),
  }
}

class Calendar extends React.Component {
  constructor(props, context) {
    super(props, context)
    const calendarDate = new Date()
    this.state = {
      currentMonth: calendarDate,
      startDate: getStartAndEndMonth(calendarDate, props.weekm).start,
      endDate: getStartAndEndMonth(calendarDate, props.weekm).end,
      weekStartOnMonday: props.weekm,
    }
  }

  componentDidMount() {
    this.props.loadMonthWorkouts(this.state.startDate, this.state.endDate)
  }

  renderHeader(localeOptions) {
    const dateFormat = 'MMM yyyy'
    return (
      <div className="header row flex-middle">
        <div className="col col-start" onClick={() => this.handlePrevMonth()}>
          <i className="fa fa-chevron-left" aria-hidden="true" />
        </div>
        <div className="col col-center">
          <span>
            {format(this.state.currentMonth, dateFormat, localeOptions)}
          </span>
        </div>
        <div className="col col-end" onClick={() => this.handleNextMonth()}>
          <i className="fa fa-chevron-right" aria-hidden="true" />
        </div>
      </div>
    )
  }

  renderDays(localeOptions) {
    const dateFormat = 'EEE'
    const days = []
    const { startDate } = this.state

    for (let i = 0; i < 7; i++) {
      days.push(
        <div className="col col-center" key={i}>
          {format(addDays(startDate, i), dateFormat, localeOptions)}
        </div>
      )
    }
    return <div className="days row">{days}</div>
  }

  filterWorkouts(day) {
    const { workouts, user } = this.props
    if (workouts) {
      return workouts
        .filter(act =>
          isSameDay(getDateWithTZ(act.workout_date, user.timezone), day)
        )
        .reverse()
    }
    return []
  }

  renderCells() {
    const { currentMonth, startDate, endDate, weekStartOnMonday } = this.state
    const { sports } = this.props

    const dateFormat = 'd'
    const rows = []

    let days = []
    let day = startDate
    let formattedDate = ''

    while (day <= endDate) {
      for (let i = 0; i < 7; i++) {
        formattedDate = format(day, dateFormat)
        const dayWorkouts = this.filterWorkouts(day)
        const isDisabled = isSameMonth(day, currentMonth) ? '' : '-disabled'
        const isWeekEnd = weekStartOnMonday
          ? [5, 6].includes(i)
          : [0, 6].includes(i)
        days.push(
          <div
            className={`col cell ${isWeekEnd ? ' weekend' : ''}${
              isToday(day) ? ' today' : ''
            }`}
            key={day}
          >
            <div className={`img${isDisabled}`}>
              <span className="number">{formattedDate}</span>
              <CalendarWorkouts
                dayWorkouts={dayWorkouts}
                isDisabled={isDisabled}
                sports={sports}
              />
            </div>
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
    const { start, end } = getStartAndEndMonth(
      calendarDate,
      this.state.weekStartOnMonday
    )
    this.setState({
      currentMonth: calendarDate,
      startDate: start,
      endDate: end,
    })
    this.props.loadMonthWorkouts(start, end)
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
    let localeOptions = {}
    switch (this.props.language) {
      case 'fr':
        localeOptions.locale = fr
        break
      case 'enUS asdf':
        localeOptions.locale = enUS
        break
      default:
        localeOptions.locale = enGB
    }
    return (
      <div className="card workout-card">
        <div className="calendar">
          {this.renderHeader(localeOptions)}
          {this.renderDays(localeOptions)}
          {this.renderCells()}
        </div>
      </div>
    )
  }
}

export default connect(
  state => ({
    workouts: state.calendarWorkouts.data,
    language: state.language,
    sports: state.sports.data,
    user: state.user,
  }),
  dispatch => ({
    loadMonthWorkouts: (start, end) => {
      const dateFormat = 'yyyy-MM-dd'
      dispatch(
        getMonthWorkouts(format(start, dateFormat), format(end, dateFormat))
      )
    },
  })
)(Calendar)
