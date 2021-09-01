import React from 'react'
import { Helmet } from 'react-helmet'

export default function AccessDenied(props) {
  const { t } = props
  return (
    <div>
      <Helmet>
        <title>FitTrackee - {t('Access denied')}</title>
      </Helmet>
      <div className="row">
        <div className="col-2" />
        <div className="card col-8">
          <div className="card-body">
            <div className="text-center">
              {t("You don't have permissions to access this page.")}
            </div>
          </div>
        </div>
        <div className="col-2" />
      </div>
    </div>
  )
}
