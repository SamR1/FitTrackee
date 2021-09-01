import React from 'react'
import { useTranslation } from 'react-i18next'

export default function CustomModal(props) {
  const { t } = useTranslation()
  return (
    <div className="custom-modal-backdrop">
      <div className="custom-modal">
        <div className="modal-content">
          <div className="modal-header">
            <h5 className="modal-title">{props.title}</h5>
            <button
              type="button"
              className="close"
              aria-label="Close"
              onClick={() => props.close()}
            >
              <span aria-hidden="true">&times;</span>
            </button>
          </div>
          <div className="modal-body">
            <p>{props.text}</p>
          </div>
          <div className="modal-footer">
            <button
              type="button"
              className="btn btn-primary"
              onClick={() => props.confirm()}
            >
              {t('common:Yes')}
            </button>
            <button
              type="button"
              className="btn btn-secondary"
              onClick={() => props.close()}
            >
              {t('common:No')}
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
