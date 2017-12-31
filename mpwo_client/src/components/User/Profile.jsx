import React from 'react'
import { connect } from 'react-redux'

function Profile ({ user }) {
  return (
    <div className="container">
      <h1 className="page-title">Profile</h1>
      <div className="row">
        <div className="col-md-8">
          <div className="card">
            <div className="card-header">
              {user.username}
            </div>
            <div className="card-body">
              <div className="row">
                <div className="col-md-8">
                  <p>Email : {user.email}</p>
                  <p>Registration date : {user.createdAt}</p>
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
  )
}

export default connect(
  state => ({
    user: state.user,
  })
)(Profile)
