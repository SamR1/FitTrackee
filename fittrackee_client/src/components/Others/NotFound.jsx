import React from 'react'
import { Helmet } from 'react-helmet'

export default function NotFound () {
  return (
    <div>
      <Helmet>
        <title>fittrackee - 404</title>
      </Helmet>
        <h1 className="page-title">Page not found</h1>
    </div>
  )
}
