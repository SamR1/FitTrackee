import React from 'react'
import { Helmet } from 'react-helmet'

import AdminStats from './AdminStats'

export default function AdminDashboard() {
  return (
    <div>
      <Helmet>
        <title>FitTrackee - Administration</title>
      </Helmet>
      <div className="card activity-card">
        <div className="card-header">
          <strong>FitTrackee administration</strong>
        </div>
        <div className="card-body">
          <AdminStats />
        </div>
      </div>
    </div>
  )
}
