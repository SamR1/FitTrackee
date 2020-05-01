import React from 'react'

export default class Message extends React.PureComponent {
  render() {
    const { message, messages, t } = this.props
    const singleMessage =
      message === '' || !message
        ? ''
        : message.split('|').length > 1
        ? `${t(`messages:${message.split('|')[0]}`)}: ${t(
            `messages:${message.split('|')[1]}`
          )}`
        : t(`messages:${message}`)
    return (
      <div className="error-message">
        {singleMessage !== '' && <code>{singleMessage}</code>}
        {messages && messages.length > 0 && (
          <code>
            <ul>
              {messages.map(msg => (
                <li key={msg.id}>{t(`messages:${msg.value}`)}</li>
              ))}
            </ul>
          </code>
        )}
      </div>
    )
  }
}
