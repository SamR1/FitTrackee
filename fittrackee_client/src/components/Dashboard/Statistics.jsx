import { endOfMonth, startOfMonth } from 'date-fns'
import React from 'react'

import Stats from '../Common/Stats'


export default class Statistics extends React.Component {
  constructor(props, context) {
    super(props, context)
    const date = new Date()
    this.state = {
      start: startOfMonth(date),
      end: endOfMonth(date),
      duration: 'week',
      type: 'by_time',
    }
  }

  render() {
    return (
      <div className="card activity-card">
        <div className="card-header">
          This month
        </div>
        <div className="card-body">
          <Stats statsParams={this.state} />
        </div>
      </div>
    )
  }
}
