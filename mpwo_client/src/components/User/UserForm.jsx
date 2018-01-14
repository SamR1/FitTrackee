import React from 'react'
import { connect } from 'react-redux'
import { Redirect } from 'react-router-dom'

import Form from './Form'
import {
  emptyForm,
  handleFormChange,
  handleUserFormSubmit
} from '../../actions'
import { isLoggedIn } from '../../utils'

class UserForm extends React.Component {

  componentWillReceiveProps(nextProps) {
    if (
      (nextProps.location.pathname !== this.props.location.pathname)
    ) {
      this.props.onEmptyForm()
    }
  }

  render() {
    const {
      formData,
      formType,
      message,
      messages,
      onHandleFormChange,
      onHandleUserFormSubmit
    } = this.props
    return (
      <div>
        {isLoggedIn() ? (
          <Redirect to="/" />
        ) : (
          <div>
            {message !== '' && (
              <code>{message}</code>
            )}
            {messages.length > 0 && (
              <code>
                <ul>
                  {messages.map(msg => (
                    <li key={msg.id}>
                      {msg.value}
                    </li>
                  ))}
                </ul>
              </code>
            )}
            <Form
              formType={formType}
              userForm={formData}
              onHandleFormChange={event => onHandleFormChange(event)}
              handleUserFormSubmit={event =>
                onHandleUserFormSubmit(event, formType)
              }
            />
          </div>
        )}
      </div>
    )
  }
}
export default connect(
  state => ({
    formData: state.formData.formData,
    location: state.router.location,
    message: state.message,
    messages: state.messages,
  }),
  dispatch => ({
    onEmptyForm: () => {
      dispatch(emptyForm())
    },
    onHandleFormChange: event => {
      dispatch(handleFormChange(event.target.name, event.target.value))
    },
    onHandleUserFormSubmit: (event, formType) => {
      dispatch(handleUserFormSubmit(event, formType))
    },
  })
)(UserForm)
