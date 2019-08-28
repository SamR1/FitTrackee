import React from 'react'
import { Helmet } from 'react-helmet'

export default function AccessDenied() {
  return (
    <div>
      <Helmet>
        <title>FitTrackee - Access denied</title>
      </Helmet>
      <h1 className="page-title">Access denied</h1>
      <p className="App-center">
        {"You don't have permissions to access this page."}
      </p>
    </div>
  )
}
