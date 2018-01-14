import React from 'react'
import { Helmet } from 'react-helmet'

export default function Form (props) {
  return (
    <div>
      <Helmet>
        <title>mpwo - {props.formType}</title>
      </Helmet>
      <h1 className="page-title">{props.formType}</h1>
      <div className="container">
      <div className="row">
        <div className="col-md-3" />
        <div className="col-md-6">
          <hr /><br />
          <form onSubmit={event =>
            props.handleUserFormSubmit(event, props.formType)}
          >
            {props.formType === 'Register' &&
            <div className="form-group">
              <input
                className="form-control input-lg"
                name="username"
                placeholder="Enter a username"
                required
                type="text"
                value={props.userForm.username}
                onChange={props.onHandleFormChange}
              />
            </div>
            }
            <div className="form-group">
              <input
                className="form-control input-lg"
                name="email"
                placeholder="Enter an email address"
                required
                type="email"
                value={props.userForm.email}
                onChange={props.onHandleFormChange}
              />
            </div>
            <div className="form-group">
              <input
                className="form-control input-lg"
                name="password"
                placeholder="Enter a password"
                required
                type="password"
                value={props.userForm.password}
                onChange={props.onHandleFormChange}
              />
            </div>
            {props.formType === 'Register' &&
            <div className="form-group">
              <input
                className="form-control input-lg"
                name="passwordConf"
                placeholder="Enter the password confirmation"
                required
                type="password"
                value={props.userForm.passwordConf}
                onChange={props.onHandleFormChange}
              />
            </div>
            }
            <input
              type="submit"
              className="btn btn-primary btn-lg btn-block"
              value="Submit"
            />
          </form>
        </div>
        <div className="col-md-3" />
      </div>
    </div>
    </div>
  )
}
