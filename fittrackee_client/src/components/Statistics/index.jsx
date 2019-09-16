import {
  endOfMonth,
  endOfWeek,
  endOfYear,
  startOfMonth,
  startOfYear,
  startOfWeek,
  addMonths,
  addWeeks,
  addYears,
  subMonths,
  subWeeks,
  subYears,
} from 'date-fns'
import React from 'react'
import { Helmet } from 'react-helmet'
import { withTranslation } from 'react-i18next'
import { connect } from 'react-redux'

import { activityColors, translateSports } from '../../utils/activities'
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
      },
    }
  }

  componentDidUpdate(prevProps) {
    if (this.props.sports !== prevProps.sports) {
      this.updateDisplayedSports()
    }
  }

  updateDisplayedSports() {
    const { sports } = this.props
    this.setState({ displayedSports: sports.map(sport => sport.id) })
  }

  handleOnChangeDuration(e) {
    const duration = e.target.name

    const date = new Date()
    const start =
      duration === 'year'
        ? startOfYear(subYears(date, 9))
        : duration === 'week'
        ? startOfMonth(subMonths(date, 2))
        : startOfMonth(subMonths(date, 11))
    const end =
      duration === 'year'
        ? endOfYear(date)
        : duration === 'week'
        ? endOfWeek(date)
        : endOfMonth(date)
    this.setState({ statsParams: { duration, end, start, type: 'by_time' } })
  }

  handleOnChangeSports(sportId) {
    const { displayedSports } = this.state
    if (displayedSports.includes(sportId)) {
      this.setState({
        displayedSports: displayedSports.filter(s => s !== sportId),
      })
    } else {
      this.setState({ displayedSports: displayedSports.concat([sportId]) })
    }
  }

  handleOnClickArrows(forward) {
    const { start, end, duration } = this.state.statsParams
    let newStart, newEnd
    if (forward) {
      newStart =
        duration === 'year'
          ? startOfYear(subYears(start, 1))
          : duration === 'week'
          ? startOfWeek(subWeeks(start, 1))
          : startOfMonth(subMonths(start, 1))
      newEnd =
        duration === 'year'
          ? endOfYear(subYears(end, 1))
          : duration === 'week'
          ? endOfWeek(subWeeks(end, 1))
          : endOfMonth(subMonths(end, 1))
    } else {
      newStart =
        duration === 'year'
          ? startOfYear(addYears(start, 1))
          : duration === 'week'
          ? startOfWeek(addWeeks(start, 1))
          : startOfMonth(addMonths(start, 1))
      newEnd =
        duration === 'year'
          ? endOfYear(addYears(end, 1))
          : duration === 'week'
          ? endOfWeek(addWeeks(end, 1))
          : endOfMonth(addMonths(end, 1))
    }
    this.setState({
      statsParams: { duration, end: newEnd, start: newStart, type: 'by_time' },
    })
  }

  render() {
    const { displayedSports, statsParams } = this.state
    const { sports, t } = this.props
    const translatedSports = translateSports(sports, t)
    return (
      <>
        <Helmet>
          <title>FitTrackee - {t('statistics:Statistics')}</title>
        </Helmet>
        <div className="container dashboard">
          <div className="card activity-card">
            <div className="card-header">{t('statistics:Statistics')}</div>
            <div className="card-body">
              <div className="chart-filters row">
                <div className="col chart-arrows">
                  <p className="text-center">
                    <i
                      className="fa fa-chevron-left"
                      aria-hidden="true"
                      onClick={() => this.handleOnClickArrows(true)}
                    />
                  </p>
                </div>
                <div className="col-md-3 time-frames justify-content-around">
                  {durations.map(d => (
                    <div className="time-frame" key={d}>
                      <label>
                        <input
                          type="radio"
                          id={d}
                          name={d}
                          checked={d === statsParams.duration}
                          onChange={e => this.handleOnChangeDuration(e)}
                        />
                        <span>{t(`statistics:${d}`)}</span>
                      </label>
                    </div>
                  ))}
                </div>
                <div className="col chart-arrows">
                  <p className="text-center">
                    <i
                      className="fa fa-chevron-right"
                      aria-hidden="true"
                      onClick={() => this.handleOnClickArrows(false)}
                    />
                  </p>
                </div>
              </div>
              <Stats
                displayEmpty
                displayedSports={displayedSports}
                statsParams={statsParams}
                t={t}
              />
              <div className="row chart-activities">
                {translatedSports.map(sport => (
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
      </>
    )
  }
}

export default withTranslation()(
  connect(state => ({
    sports: state.sports.data,
  }))(Statistics)
)
