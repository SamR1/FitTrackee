import React from 'react'
import { connect } from 'react-redux'
import { Helmet } from 'react-helmet'

import Config from './Config'
import ConfigForm from './ConfigForm'
import Message from '../../Common/Message'

class AdminApplication extends React.Component {
  constructor(props, context) {
    super(props, context)
    this.state = {
      isInEdition: false,
    }
  }

  render() {
    const { appConfig, message, t } = this.props
    const { isInEdition } = this.state
    return (
      <div>
        <Helmet>
          <title>FitTrackee - {t('administration:Administration')}</title>
        </Helmet>
        {message && <Message message={message} t={t} />}
        {isInEdition ? (
          <ConfigForm
            appConfig={appConfig}
            message={message}
            updateIsInEdition={() => {
              this.setState({ isInEdition: false })
            }}
            t={t}
          />
        ) : (
          <Config
            appConfig={appConfig}
            message={message}
            t={t}
            updateIsInEdition={() => {
              this.setState({ isInEdition: true })
            }}
          />
        )}
      </div>
    )
  }
}

export default connect(state => ({
  appConfig: state.application.config,
  message: state.message,
  user: state.user,
}))(AdminApplication)
