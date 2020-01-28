import React from 'react'
import { Link } from 'react-router-dom'

import { recordsLabels } from '../../utils/activities'

export default class CalendarActivities extends React.PureComponent {
  render() {
    const { dayActivities, isDisabled, sports } = this.props
    return (
      <>
        {dayActivities.map(act => (
          <Link key={act.id} to={`/activities/${act.id}`}>
            <>
              <img
                alt="activity sport logo"
                className={`activity-sport ${isDisabled}`}
                src={sports.filter(s => s.id === act.sport_id).map(s => s.img)}
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
            </>
          </Link>
        ))}
      </>
    )
  }
}
