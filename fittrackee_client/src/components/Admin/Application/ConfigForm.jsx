import React from 'react'
import { connect } from 'react-redux'
import { Helmet } from 'react-helmet'

import Message from '../../Common/Message'
import { updateAppConfig } from '../../../actions/application'
import { getFileSizeInMB } from '../../../utils'

class AdminApplication extends React.Component {
  constructor(props, context) {
    super(props, context)
    this.state = {
      formData: {},
    }
  }
  componentDidMount() {
    this.initForm()
  }

  initForm() {
    const { appConfig } = this.props
    const formData = {}
    Object.keys(appConfig).map(k =>
      appConfig[k] === null
        ? (formData[k] = '')
        : ['max_single_file_size', 'max_zip_file_size'].includes(k)
        ? (formData[k] = getFileSizeInMB(appConfig[k]))
        : (formData[k] = appConfig[k])
    )
    this.setState({ formData })
  }

  handleFormChange(e) {
    const { formData } = this.state
    if (e.target.name === 'registration') {
      formData[e.target.name] = e.target.checked
    } else {
      formData[e.target.name] = +e.target.value
    }
    this.setState(formData)
  }

  render() {
    const {
      message,
      onHandleConfigFormSubmit,
      t,
      updateIsInEdition,
    } = this.props
    const { formData } = this.state
    return (
      <div>
        <Helmet>
          <title>
            FitTrackee - {t('administration:Application configuration')}
          </title>
        </Helmet>
        {message && <Message message={message} t={t} />}
        {Object.keys(formData).length > 0 && (
          <div className="container">
            <div className="row">
              <div className="col-md-12">
                <div className="card">
                  <div className="card-header">
                    {t('administration:Application configuration')}
                  </div>
                  <div className="card-body">
                    <form
                      className="app-config-form"
                      onSubmit={event => {
                        event.preventDefault()
                        onHandleConfigFormSubmit(formData)
                        updateIsInEdition()
                      }}
                    >
                      <div className="form-group row">
                        <label
                          className="col-sm-6 col-form-label"
                          htmlFor="registration"
                        >
                          {t('administration:Enable registration')}:
                        </label>
                        <input
                          className="col-sm-5"
                          id="registration"
                          name="registration"
                          type="checkbox"
                          checked={formData.registration}
                          onChange={e => this.handleFormChange(e)}
                        />
                      </div>
                      <div className="form-group row">
                        <label
                          className="col-sm-6 col-form-label"
                          htmlFor="max_users"
                        >
                          {t('administration:Max. number of active users')}:
                        </label>
                        <input
                          className="col-sm-5"
                          id="max_users"
                          name="max_users"
                          type="number"
                          min="0"
                          value={formData.max_users}
                          onChange={e => this.handleFormChange(e)}
                        />
                      </div>
                      <div className="form-group row">
                        <label
                          className="col-sm-6 col-form-label"
                          htmlFor="max_single_file_size"
                        >
                          {t(
                            'administration:Max. size of uploaded files (in Mb)'
                          )}
                          :
                        </label>
                        <input
                          className="col-sm-5"
                          id="max_single_file_size"
                          name="max_single_file_size"
                          type="number"
                          step="0.1"
                          min="0"
                          value={formData.max_single_file_size}
                          onChange={e => this.handleFormChange(e)}
                        />
                      </div>
                      <div className="form-group row">
                        <label
                          className="col-sm-6 col-form-label"
                          htmlFor="max_zip_file_size"
                        >
                          {t('administration:Max. size of zip archive (in Mb)')}
                          :
                        </label>
                        <input
                          className="col-sm-5"
                          id="max_zip_file_size"
                          name="max_zip_file_size"
                          type="number"
                          step="0.1"
                          min="0"
                          value={formData.max_zip_file_size}
                          onChange={e => this.handleFormChange(e)}
                        />
                      </div>
                      <div className="form-group row">
                        <label
                          className="col-sm-6 col-form-label"
                          htmlFor="gpx_limit_import"
                        >
                          {t('administration:Max. files of zip archive')}
                        </label>
                        <input
                          className="col-sm-5"
                          id="gpx_limit_import"
                          name="gpx_limit_import"
                          type="number"
                          min="0"
                          value={formData.gpx_limit_import}
                          onChange={e => this.handleFormChange(e)}
                        />
                      </div>
                      <input
                        type="submit"
                        className="btn btn-primary btn-lg btn-block"
                        value={t('common:Submit')}
                      />
                      <input
                        type="submit"
                        className="btn btn-secondary btn-lg btn-block"
                        onClick={() => updateIsInEdition()}
                        value={t('common:Cancel')}
                      />
                    </form>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    )
  }
}

export default connect(
  () => ({}),
  dispatch => ({
    onHandleConfigFormSubmit: formData => {
      formData.max_single_file_size *= 1048576
      formData.max_zip_file_size *= 1048576
      dispatch(updateAppConfig(formData))
    },
  })
)(AdminApplication)
