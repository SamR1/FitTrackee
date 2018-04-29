import { format } from 'date-fns'
import React from 'react'
import { Helmet } from 'react-helmet'
import { connect } from 'react-redux'
import { Link } from 'react-router-dom'

import { deletePicture, uploadPicture } from '../../actions'
import { apiUrl } from '../../utils'

function Profile ({ message, onDeletePicture, onUploadPicture, user }) {
  return (
    <div>
      <Helmet>
        <title>mpwo - {user.username} - Profile</title>
      </Helmet>
      { message !== '' && (
        <code>{message}</code>
      )}
      <div className="container">
        <h1 className="page-title">Profile</h1>
        <div className="row">
          <div className="col-md-12">
            <div className="card">
              <div className="card-header userName">
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
                    <p>Email: {user.email}</p>
                    <p>Registration Date: {
                         format(new Date(user.createdAt), 'DD/MM/YYYY HH:mm')
                       }</p>
                    <p>First Name: {user.firstName}</p>
                    <p>Last Name: {user.lastName}</p>
                    <p>Birth Date: {user.birthDate}</p>
                    <p>Location: {user.location}</p>
                    <p>Bio: {user.bio}</p>
                  </div>
                  <div className="col-md-4">
                    { user.picture === true && (
                    <div>
                      <img
                        alt="Profile"
                        src={`${apiUrl}users/${user.id}/picture` +
                             `?${Date.now()}`}
                        className="img-fluid App-profile-img-small"
                      />
                      <br />
                      <button
                        type="submit"
                        onClick={() => onDeletePicture()}
                      >
                        Delete picture
                      </button>
                      <br /><br />
                    </div>
                    )}
                    <form
                      encType="multipart/form-data"
                      onSubmit={event => onUploadPicture(event)}
                    >
                      <input
                          type="file"
                          name="picture"
                          accept=".png,.jpg,.gif"
                      />
                      <br />
                      <button type="submit">Send</button>
                    </form>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default connect(
  state => ({
    message: state.message,
    user: state.user,
  }),
  dispatch => ({
    onDeletePicture: () => {
      dispatch(deletePicture())
    },
    onUploadPicture: event => {
      dispatch(uploadPicture(event))
    },
  })
)(Profile)
