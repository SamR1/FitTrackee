import { format } from 'date-fns'
import React from 'react'
import { Helmet } from 'react-helmet'
import { withTranslation } from 'react-i18next'
import { connect } from 'react-redux'
import TimezonePicker from 'react-timezone'

import { handleProfileFormSubmit } from '../../actions/user'
import { history } from '../../index'
import { languages } from '../NavBar/LanguageDropdown'

class ProfileEdit extends React.Component {
  constructor(props, context) {
    super(props, context)
    this.state = {
      formData: {},
    }
  }

  componentDidMount() {
    this.initForm()
  }

  componentDidUpdate(prevProps) {
    if (prevProps.user !== this.props.user) {
      this.initForm()
    }
  }

  initForm() {
    const { user } = this.props
    const formData = {}
    Object.keys(user).map(k =>
      user[k] === null
        ? (formData[k] = '')
        : k === 'birth_date'
        ? (formData[k] = format(new Date(user[k]), 'yyyy-MM-DD'))
        : (formData[k] = user[k])
    )
    this.setState({ formData })
  }

  handleFormChange(e) {
    const { formData } = this.state
    if (e.target.name === 'weekm') {
      formData.weekm = e.target.value === 'Monday'
    } else {
      formData[e.target.name] = e.target.value
    }
    this.setState(formData)
  }

  render() {
    const { onHandleProfileFormSubmit, message, t, user } = this.props
    const { formData } = this.state
    return (
      <div>
        <Helmet>
          <title>FitTrackee - {t('user:Profile Edition')}</title>
        </Helmet>
        {message !== '' && <code>{t(`messages:${message}`)}</code>}
        {formData.isAuthenticated && (
          <div className="container">
            <h1 className="page-title">{t('user:Profile Edition')}</h1>
            <div className="row">
              <div className="col-md-2" />
              <div className="col-md-8">
                <div className="card">
                  <div className="card-header">{user.username}</div>
                  <div className="card-body">
                    <div className="row">
                      <div className="col-md-12">
                        <form
                          onSubmit={event => {
                            event.preventDefault()
                            onHandleProfileFormSubmit(formData)
                          }}
                        >
                          <div className="form-group">
                            <label>
                              {t('user:Email')}:
                              <input
                                name="email"
                                className="form-control input-lg"
                                type="text"
                                value={formData.email}
                                readOnly
                              />
                            </label>
                          </div>
                          <div className="form-group">
                            <label>
                              {t('user:Registration Date')}:
                              <input
                                name="createdAt"
                                className="form-control input-lg"
                                type="text"
                                value={formData.created_at}
                                disabled
                              />
                            </label>
                          </div>
                          <div className="form-group">
                            <label>
                              {t('user:Password')}:
                              <input
                                name="password"
                                className="form-control input-lg"
                                type="password"
                                onChange={e => this.handleFormChange(e)}
                              />
                            </label>
                          </div>
                          <div className="form-group">
                            <label>
                              {t('user:Password Confirmation')}:
                              <input
                                name="password_conf"
                                className="form-control input-lg"
                                type="password"
                                onChange={e => this.handleFormChange(e)}
                              />
                            </label>
                          </div>
                          <hr />
                          <div className="form-group">
                            <label>
                              {t('user:First Name')}:
                              <input
                                name="first_name"
                                className="form-control input-lg"
                                type="text"
                                value={formData.first_name}
                                onChange={e => this.handleFormChange(e)}
                              />
                            </label>
                          </div>
                          <div className="form-group">
                            <label>
                              {t('user:Last Name')}:
                              <input
                                name="last_name"
                                className="form-control input-lg"
                                type="text"
                                value={formData.last_name}
                                onChange={e => this.handleFormChange(e)}
                              />
                            </label>
                          </div>
                          <div className="form-group">
                            <label>
                              {t('user:Birth Date')}
                              <input
                                name="birth_date"
                                className="form-control input-lg"
                                type="date"
                                value={formData.birth_date}
                                onChange={e => this.handleFormChange(e)}
                              />
                            </label>
                          </div>
                          <div className="form-group">
                            <label>
                              {t('user:Location')}:
                              <input
                                name="location"
                                className="form-control input-lg"
                                type="text"
                                value={formData.location}
                                onChange={e => this.handleFormChange(e)}
                              />
                            </label>
                          </div>
                          <div className="form-group">
                            <label>
                              {t('user:Bio')}:
                              <textarea
                                name="bio"
                                className="form-control input-lg"
                                maxLength="200"
                                value={formData.bio}
                                onChange={e => this.handleFormChange(e)}
                              />
                            </label>
                          </div>
                          <div className="form-group">
                            <label>
                              {t('user:Language')}:
                              <select
                                name="language"
                                className="form-control input-lg"
                                value={formData.language}
                                onChange={e => this.handleFormChange(e)}
                              >
                                {languages.map(lang => (
                                  <option value={lang.name} key={lang.name}>
                                    {lang.name}
                                  </option>
                                ))}
                              </select>
                            </label>
                          </div>
                          <div className="form-group">
                            <label>
                              {t('user:Timezone')}:
                              <TimezonePicker
                                className="form-control timezone-custom-height"
                                onChange={tz => {
                                  const e = {
                                    target: {
                                      name: 'timezone',
                                      value: tz ? tz : 'Europe/Paris',
                                    },
                                  }
                                  this.handleFormChange(e)
                                }}
                                value={formData.timezone}
                              />
                            </label>
                          </div>
                          <div className="form-group">
                            <label>
                              {t('user:First day of week')}:
                              <select
                                name="weekm"
                                className="form-control input-lg"
                                value={formData.weekm ? 'Monday' : 'Sunday'}
                                onChange={e => this.handleFormChange(e)}
                              >
                                <option value="Sunday">
                                  {t('user:Sunday')}
                                </option>
                                <option value="Monday">
                                  {t('user:Monday')}
                                </option>
                              </select>
                            </label>
                          </div>
                          <input
                            type="submit"
                            className="btn btn-primary btn-lg btn-block"
                            value={t('common:Submit')}
                          />
                          <input
                            type="submit"
                            className="btn btn-secondary btn-lg btn-block"
                            onClick={() => history.push('/profile')}
                            value={t('common:Cancel')}
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
      user: state.user,
    }),
    dispatch => ({
      onHandleProfileFormSubmit: formData => {
        dispatch(handleProfileFormSubmit(formData))
      },
    })
  )(ProfileEdit)
)
