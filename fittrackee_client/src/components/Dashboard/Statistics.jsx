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
    const { t } = this.props
    return (
      <div className="card workout-card">
        <div className="card-header">{t('dashboard:This month')}</div>
        <div className="card-body">
          <Stats displayEmpty={false} statsParams={this.state} t={t} />
        </div>
      </div>
    )
  }
}
