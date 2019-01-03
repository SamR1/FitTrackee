import { endOfMonth, startOfMonth, subMonths } from 'date-fns'
import React from 'react'

import Stats from '../Common/Stats'


export default class Statistics extends React.Component {
  constructor(props, context) {
    super(props, context)
    const date = new Date()
    this.state = {
      start: startOfMonth(subMonths(date, 12)),
      end: endOfMonth(date),
      duration: 'month',
      type: 'by_time',
    }
  }

  render() {
    return (
      <div className="container dashboard">
        <div className="card activity-card">
          <div className="card-header">
            Statistics
          </div>
          <div className="card-body">
            <Stats statsParams={this.state} />
          </div>
        </div>
      </div>
    )
  }
}
