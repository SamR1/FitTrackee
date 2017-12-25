import React from 'react'


export default function Form (props) {
  return (
    <div>
      <h1>{props.formType}</h1>
      <hr /><br />
      <form onSubmit={event =>
          props.handleUserFormSubmit(event, props.formType)}
      >
        {props.formType === 'Register' &&
          <div className="form-group">
            <input
              name="username"
              className="form-control input-lg"
              type="text"
              placeholder="Enter a username"
              required
              onChange={props.onHandleFormChange}
            />
          </div>
        }
        <div className="form-group">
          <input
            name="email"
            className="form-control input-lg"
            type="email"
            placeholder="Enter an email address"
            required
            onChange={props.onHandleFormChange}
          />
        </div>
        <div className="form-group">
          <input
            name="password"
            className="form-control input-lg"
            type="password"
            placeholder="Enter a password"
            required
            onChange={props.onHandleFormChange}
          />
        </div>
        <input
          type="submit"
          className="btn btn-primary btn-lg btn-block"
          value="Submit"
        />
      </form>
    </div>
  )
}
