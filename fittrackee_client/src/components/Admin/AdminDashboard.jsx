import React from 'react'
import { Link } from 'react-router-dom'
import { Helmet } from 'react-helmet'

import AdminStats from './AdminStats'
import { capitalize } from '../../utils'

const menuItems = ['application', 'sports', 'users']

export default function AdminDashboard(props) {
  const { t } = props
  return (
    <>
      <Helmet>
        <title>{t('administration:FitTrackee administration')}</title>
      </Helmet>
      <div className="card activity-card">
        <div className="card-header">{t('administration:Administration')}</div>
        <div className="card-body">
          <AdminStats />
          <ul className="admin-items">
            {menuItems.map(item => (
              <li key={item}>
                <Link
                  to={{
                    pathname: `/admin/${item}`,
                  }}
                >
                  {t(`administration:${capitalize(item)}`)}
                </Link>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </>
  )
}
