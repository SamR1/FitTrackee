import React from 'react'
import { connect } from 'react-redux'
import { Redirect } from 'react-router-dom'

import Form from './Form'
import { handleFormChange, handleUserFormSubmit } from '../../actions'
import { isLoggedIn } from '../../utils'

function UserForm(props) {
  return (
    <div>
      {isLoggedIn() ? (
        <Redirect to="/" />
      ) : (
        <div>
          { props.message !== '' && (
            <code>{props.message}</code>
          )}
          { props.messages.length > 0 && (
            <code>
              <ul>
                {props.messages.map(msg => (
                  <li key={msg.id}>
                    {msg.value}
                  </li>
                ))}
              </ul>
            </code>
          )}
          <Form
            formType={props.formType}
            userForm={props.formData}
            onHandleFormChange={event => props.onHandleFormChange(event)}
            handleUserFormSubmit={(event, formType) =>
              props.onHandleUserFormSubmit(event, formType)}
          />
        </div>
      )}
    </div>
  )
}
export default connect(
  state => ({
    formData: state.formData,
    message: state.message,
    messages: state.messages,
  }),
  dispatch => ({
    onHandleFormChange: event => {
      dispatch(handleFormChange(event.target.name, event.target.value))
    },
    onHandleUserFormSubmit: (event, formType) => {
      dispatch(handleUserFormSubmit(event, formType))
    },
  })
)(UserForm)
