import React from 'react'
import { Helmet } from 'react-helmet'
import { useTranslation } from 'react-i18next'

export default function NotFound() {
  const { t } = useTranslation()
  return (
    <div>
      <Helmet>
        <title>fittrackee - 404</title>
      </Helmet>
      <h1 className="page-title">{t('Page not found')}</h1>
    </div>
  )
}
