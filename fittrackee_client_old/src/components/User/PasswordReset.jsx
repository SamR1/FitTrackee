import React from 'react'
import { Trans, useTranslation } from 'react-i18next'
import { Link } from 'react-router-dom'

import { ReactComponent as Password } from '../../images/password.svg'
import { ReactComponent as MailSend } from '../../images/mail-send.svg'

export default function PasswordReset(props) {
  const { t } = useTranslation()
  const { action } = props
  return (
    <div className="container dashboard">
      <div className="row">
        <div className="col-2" />
        <div className="card col-8">
          <div className="card-body">
            <div className="text-center ">
              {action === 'sent' && (
                <>
                  <div className="svg-icon">
                    <MailSend />
                  </div>
                  {t(
                    // eslint-disable-next-line max-len
                    "user:Check your email. If your address is in our database, you'll received an email with a link to reset your password."
                  )}
                </>
              )}
              {action === 'updated' && (
                <>
                  <div className="svg-icon">
                    <Password />
                  </div>
                  <Trans i18nKey="user:updatedPasswordText">
                    {/* prettier-ignore */}
                    Your password have been updated. Click
                    <Link to="/login">here</Link> to log in.
                  </Trans>
                </>
              )}
            </div>
          </div>
        </div>
        <div className="col-2" />
      </div>
    </div>
  )
}
