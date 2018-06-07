import React from 'react'
import { Helmet } from 'react-helmet'
import { Link } from 'react-router-dom'

export default function AdminMenu () {
  return (
    <div>
      <Helmet>
        <title>FitTrackee - Admin - Sports</title>
      </Helmet>
      <h1 className="page-title">Administration</h1>
      <div className="container">
        <div className="row">
          <div className="col-md-2" />
          <div className="col-md-8 card">
            <div className="card-body">
              <ul className="admin-items">
                <li>
                  <Link
                    to={{
                      pathname: '/admin/sports',
                    }}
                  >
                    Sports
                  </Link>
                </li>
              </ul>
            </div>
          </div>
          <div className="col-md-2" />
        </div>
      </div>
    </div>
  )
}
