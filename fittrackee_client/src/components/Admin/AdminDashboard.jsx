import React from 'react'
import { Link } from 'react-router-dom'
import { Helmet } from 'react-helmet'

import AdminStats from './AdminStats'

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
          <br />
          <dl className="admin-items">
            <dt>
              <Link
                to={{
                  pathname: '/admin/application',
                }}
              >
                {t('administration:Application')}
              </Link>
            </dt>
            <dd>
              {t(
                'administration:Update application configuration ' +
                  '(maximum number of registered users, maximum files size).'
              )}{' '}
            </dd>
            <br />
            <dt>
              <Link
                to={{
                  pathname: '/admin/sports',
                }}
              >
                {t('administration:Sports')}
              </Link>
            </dt>
            <dd>{t('administration:Enable/disable sports.')}</dd>
            <br />
            <dt>
              <Link
                to={{
                  pathname: '/admin/users',
                }}
              >
                {t('administration:Users')}
              </Link>
            </dt>
            <dd>
              {t(
                'administration:Add/remove admin rigths, ' +
                  'delete user account.'
              )}
            </dd>
          </dl>
        </div>
      </div>
    </>
  )
}
