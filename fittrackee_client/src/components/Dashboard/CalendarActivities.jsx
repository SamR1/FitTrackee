import React from 'react'

import CalendarActivity from './CalendarActivity'

export default class CalendarActivities extends React.Component {
  constructor(props, context) {
    super(props, context)
    this.state = {
      isHidden: true,
    }
  }

  handleDisplayMore() {
    this.setState({
      isHidden: !this.state.isHidden,
    })
  }

  render() {
    const { dayActivities, isDisabled, sports } = this.props
    const { isHidden } = this.state
    return (
      <div>
        {dayActivities.map(act => (
          <CalendarActivity
            key={act.id}
            activity={act}
            isDisabled={isDisabled}
            isMore=""
            sportImg={sports.filter(s => s.id === act.sport_id).map(s => s.img)}
          />
        ))}
        {dayActivities.length > 2 && (
          <i
            className="fa fa-plus calendar-more"
            aria-hidden="true"
            onClick={() => this.handleDisplayMore()}
            title="show more activities"
          />
        )}
        {!isHidden && (
          <div className="calendar-display-more">
            {dayActivities.map(act => (
              <CalendarActivity
                key={act.id}
                activity={act}
                isDisabled={isDisabled}
                isMore="-more"
                sportImg={sports
                  .filter(s => s.id === act.sport_id)
                  .map(s => s.img)}
              />
            ))}
          </div>
        )}
      </div>
    )
  }
}
