import React from 'react'
import { Helmet } from 'react-helmet'
import { connect } from 'react-redux'
import { Link } from 'react-router-dom'

function Profile ({ user }) {
  return (
    <div>
      <Helmet>
        <title>mpwo - {user.username} - Profile</title>
      </Helmet>
      <div className="container">
        <h1 className="page-title">Profile</h1>
        <div className="row">
          <div className="col-md-8">
            <div className="card">
              <div className="card-header">
                {user.username} {' '}
                <Link
                  to={{
                    pathname: '/profile/edit',
                  }}
                >
                  <i className="fa fa-pencil-square-o" aria-hidden="true" />
                </Link>
              </div>
              <div className="card-body">
                <div className="row">
                  <div className="col-md-8">
                    <p>Email : {user.email}</p>
                    <p>Registration Date : {user.createdAt}</p>
                    <p>First Name : {user.firstName}</p>
                    <p>Last Name : {user.lastName}</p>
                    <p>Birth Date : {user.birthDate}</p>
                    <p>Location : {user.location}</p>
                    <p>Bio : {user.bio}</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div className="col-md-4">
            <div className="card">
              <div className="card-header">
                Last activities
              </div>
              <div className="card-body" />
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default connect(
  state => ({
    user: state.user,
  })
)(Profile)
