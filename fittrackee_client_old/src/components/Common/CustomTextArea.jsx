import React from 'react'
import { withTranslation } from 'react-i18next'
import { connect } from 'react-redux'

class CustomTextArea extends React.Component {
  constructor(props, context) {
    super(props, context)
    this.state = {
      text: props.defaultValue ? props.defaultValue : '',
    }
  }

  handleOnChange(changeEvent) {
    this.setState({ text: changeEvent.target.value })
    if (this.props.onTextChange) {
      this.props.onTextChange(changeEvent)
    }
  }

  render() {
    const { charLimit, loading, name, t } = this.props
    const { text } = this.state
    return (
      <>
        <textarea
          name={name}
          defaultValue={text}
          disabled={loading ? loading : false}
          className="form-control input-lg"
          maxLength={charLimit}
          onChange={event => this.handleOnChange(event)}
        />
        <div className="remaining-chars">
          {t('common:remaining characters')}: {text.length}/{charLimit}
        </div>
      </>
    )
  }
}

export default withTranslation()(
  connect(state => ({
    loading: state.loading,
  }))(CustomTextArea)
)
