import React from 'react'

import CalendarWorkout from './CalendarWorkout'

export default class CalendarWorkouts extends React.Component {
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
    const { dayWorkouts, isDisabled, sports } = this.props
    const { isHidden } = this.state
    return (
      <div>
        {dayWorkouts.map(act => (
          <CalendarWorkout
            key={act.id}
            workout={act}
            isDisabled={isDisabled}
            isMore=""
            sportImg={sports.filter(s => s.id === act.sport_id).map(s => s.img)}
          />
        ))}
        {dayWorkouts.length > 2 && (
          <i
            className={`fa fa-${isHidden ? 'plus' : 'times'} calendar-more`}
            aria-hidden="true"
            onClick={() => this.handleDisplayMore()}
            title="show more workouts"
          />
        )}
        {!isHidden && (
          <div className="calendar-display-more">
            {dayWorkouts.map(act => (
              <CalendarWorkout
                key={act.id}
                workout={act}
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
