import React from 'react'
import { Helmet } from 'react-helmet'
import { connect } from 'react-redux'

import {
  initProfileForm,
  updateProfileFormData,
  handleProfileFormSubmit
} from '../../actions/user'
import { history } from '../../index'


class ProfileEdit extends React.Component {
  componentDidMount() {
    this.props.initForm(this.props.user)
  }
  render () {
    const { formProfile,
            onHandleFormChange,
            onHandleProfileFormSubmit,
            message,
            user
    } = this.props
    return (
      <div>
        <Helmet>
          <title>mpwo - {user.username} - Edit Profile</title>
        </Helmet>
        { message !== '' && (
            <code>{message}</code>
          )}
        <div className="container">
          <h1 className="page-title">Profile Edition</h1>
          <div className="row">
            <div className="col-md-2" />
            <div className="col-md-8">
              <div className="card">
                <div className="card-header">
                  {user.username}
                </div>
                <div className="card-body">
                  <div className="row">
                    <div className="col-md-12">
                    <form onSubmit={event =>
                      onHandleProfileFormSubmit(event)}
                    >
                      <div className="form-group">
                        <label>Email:
                          <input
                          name="email"
                          className="form-control input-lg"
                          type="text"
                          value={user.email}
                          readOnly
                          />
                        </label>
                      </div>
                      <div className="form-group">
                        <label>
                          Registration Date:
                          <input
                            name="createdAt"
                            className="form-control input-lg"
                            type="text"
                            value={user.createdAt}
                            readOnly
                          />
                        </label>
                      </div>
                      <div className="form-group">
                        <label>
                          Password:
                          <input
                            name="password"
                            className="form-control input-lg"
                            type="password"
                            onChange={onHandleFormChange}
                          />
                        </label>
                      </div>
                        <div className="form-group">
                        <label>
                          Password Confirmation:
                          <input
                            name="passwordConf"
                            className="form-control input-lg"
                            type="password"
                            onChange={onHandleFormChange}
                          />
                        </label>
                      </div>
                      <hr />
                      <div className="form-group">
                        <label>
                          First Name:
                          <input
                            name="firstName"
                            className="form-control input-lg"
                            type="text"
                            value={formProfile.firstName}
                            onChange={onHandleFormChange}
                          />
                        </label>
                      </div>
                      <div className="form-group">
                        <label>
                          Last Name:
                          <input
                            name="lastName"
                            className="form-control input-lg"
                            type="text"
                            value={formProfile.lastName}
                            onChange={onHandleFormChange}
                          />
                        </label>
                      </div>
                      <div className="form-group">
                        <label>
                          Birth Date
                          <input
                            name="birthDate"
                            className="form-control input-lg"
                            type="date"
                            value={formProfile.birthDate}
                            onChange={onHandleFormChange}
                          />
                        </label>
                      </div>
                      <div className="form-group">
                        <label>
                          Location:
                          <input
                            name="location"
                            className="form-control input-lg"
                            type="text"
                            value={formProfile.location}
                            onChange={onHandleFormChange}
                          />
                        </label>
                      </div>
                      <div className="form-group">
                        <label>
                          Bio:
                          <textarea
                            name="bio"
                            className="form-control input-lg"
                            maxLength="200"
                            type="text"
                            value={formProfile.bio}
                            onChange={onHandleFormChange}
                          />
                        </label>
                      </div>
                      <input
                        type="submit"
                        className="btn btn-primary btn-lg btn-block"
                        value="Submit"
                      />
                      <input
                        type="submit"
                        className="btn btn-secondary btn-lg btn-block"
                        onClick={() => history.push('/profile')}
                        value="Cancel"
                      />
                    </form>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            <div className="col-md-2" />
          </div>
        </div>
      </div>
    )
  }

}

export default connect(
  state => ({
    formProfile: state.formProfile.formProfile,
    message: state.message,
    user: state.user,
  }),
  dispatch => ({
    initForm: () => {
      dispatch(initProfileForm())
    },
    onHandleFormChange: event => {
      dispatch(updateProfileFormData(event.target.name, event.target.value))
    },
    onHandleProfileFormSubmit: event => {
      dispatch(handleProfileFormSubmit(event))
    },
  })
)(ProfileEdit)
