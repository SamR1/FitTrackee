import React from 'react'
import { withTranslation } from 'react-i18next'
import { connect } from 'react-redux'
import { Redirect } from 'react-router-dom'

import Form from './Form'
import Message from '../Common/Message'
import { handleUserFormSubmit } from '../../actions/user'
import { isLoggedIn } from '../../utils'

class UserForm extends React.Component {
  constructor(props, context) {
    super(props, context)
    this.state = {
      formData: {
        username: '',
        email: '',
        password: '',
        password_conf: '',
      },
    }
  }

  componentDidUpdate(prevProps) {
    if (prevProps.location.pathname !== this.props.location.pathname) {
      this.emptyForm()
    }
  }

  emptyForm() {
    const { formData } = this.state
    Object.keys(formData).map(k => (formData[k] = ''))
    this.setState(formData)
  }

  onHandleFormChange(e) {
    const { formData } = this.state
    formData[e.target.name] = e.target.value
    this.setState(formData)
  }

  render() {
    const {
      formType,
      message,
      messages,
      onHandleUserFormSubmit,
      t,
    } = this.props
    const { formData } = this.state
    return (
      <div>
        {isLoggedIn() ? (
          <Redirect to="/" />
        ) : (
          <div>
            <Message message={message} messages={messages} t={t} />
            <Form
              formType={formType}
              userForm={formData}
              onHandleFormChange={event => this.onHandleFormChange(event)}
              handleUserFormSubmit={event => {
                event.preventDefault()
                onHandleUserFormSubmit(formData, formType)
              }}
            />
          </div>
        )}
      </div>
    )
  }
}
export default withTranslation()(
  connect(
    state => ({
      location: state.router.location,
      message: state.message,
      messages: state.messages,
    }),
    dispatch => ({
      onHandleUserFormSubmit: (formData, formType) => {
        dispatch(handleUserFormSubmit(formData, formType))
      },
    })
  )(UserForm)
)
