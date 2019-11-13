import React from 'react'
import { Helmet } from 'react-helmet'

import AdminStats from './AdminStats'

export default function AdminDashboard(props) {
  const { t } = props
  return (
    <div>
      <Helmet>
        <title>{t('administration:FitTrackee administration')}</title>
      </Helmet>
      <div className="card activity-card">
        <div className="card-header">
          <strong>{t('administration:FitTrackee administration')}</strong>
        </div>
        <div className="card-body">
          <AdminStats />
        </div>
      </div>
    </div>
  )
}
