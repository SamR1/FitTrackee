import { format } from 'date-fns'
import React from 'react'
import { Helmet } from 'react-helmet'
import { withTranslation } from 'react-i18next'
import { connect } from 'react-redux'

import Message from '../Common/Message'
import { deletePicture, uploadPicture } from '../../actions/user'
import { apiUrl, getFileSize } from '../../utils'
import { history } from '../../index'

function ProfileDetail({
  appConfig,
  displayModal,
  editable,
  isDeletable,
  message,
  onDeletePicture,
  onUploadPicture,
  pathname,
  t,
  user,
}) {
  const createdAt = user.created_at
    ? format(new Date(user.created_at), 'dd/MM/yyyy HH:mm')
    : ''
  const birthDate = user.birth_date
    ? format(new Date(user.birth_date), 'dd/MM/yyyy')
    : ''
  const fileSizeLimit = getFileSize(appConfig.max_single_file_size)
  return (
    <div>
      <Helmet>
        <title>FitTrackee - {t('user:Profile')}</title>
      </Helmet>
      <Message message={message} t={t} />
      <div className="container">
        <h1 className="page-title">{t('user:Profile')}</h1>
        <div className="row">
          <div className="col-md-12">
            <div className="card">
              <div className="card-header userName">
                <strong>{user.username}</strong>
              </div>
              <div className="card-body">
                <div className="row">
                  <div className="col-md-8">
                    <p>
                      {/* eslint-disable-next-line max-len */}
                      <span className="user-label">
                        {t('user:Email')}
                      </span>: {user.email}
                    </p>
                    <p>
                      <span className="user-label">
                        {t('user:Registration Date')}
                      </span>
                      : {createdAt}
                    </p>
                    <p>
                      <span className="user-label">{t('user:First Name')}</span>
                      : {user.first_name}
                    </p>
                    <p>
                      {/* eslint-disable-next-line max-len */}
                      <span className="user-label">
                        {t('user:Last Name')}
                      </span>: {user.last_name}
                    </p>
                    <p>
                      <span className="user-label">{t('user:Birth Date')}</span>
                      : {birthDate}
                    </p>
                    <p>
                      {/* eslint-disable-next-line max-len */}
                      <span className="user-label">
                        {t('user:Location')}
                      </span>: {user.location}
                    </p>
                    <p>
                      <span className="user-label">{t('user:Bio')}</span>:{' '}
                      <span className="user-bio">{user.bio}</span>
                    </p>
                    <p>
                      {/* eslint-disable-next-line max-len */}
                      <span className="user-label">
                        {t('user:Language')}
                      </span>: {user.language}
                    </p>
                    <p>
                      {/* eslint-disable-next-line max-len */}
                      <span className="user-label">
                        {t('user:Timezone')}
                      </span>: {user.timezone}
                    </p>
                    <p>
                      <span className="user-label">
                        {t('user:First day of week')}
                      </span>
                      : {user.weekm ? t('user:Monday') : t('user:Sunday')}
                    </p>
                  </div>
                  <div className="col-md-4">
                    {user.picture === true && (
                      <div>
                        <img
                          alt="Profile"
                          src={
                            `${apiUrl}users/${user.username}/picture` +
                            `?${Date.now()}`
                          }
                          className="img-fluid App-profile-img-small"
                        />
                        {editable && (
                          <>
                            <br />
                            <button
                              type="submit"
                              onClick={() => onDeletePicture()}
                            >
                              {t('user:Delete picture')}
                            </button>
                            <br />
                            <br />
                          </>
                        )}
                      </div>
                    )}
                    {editable && (
                      <form
                        encType="multipart/form-data"
                        onSubmit={event => onUploadPicture(event)}
                      >
                        <input
                          type="file"
                          name="picture"
                          accept=".png,.jpg,.gif"
                        />
                        <br />
                        <button type="submit">{t('user:Send')}</button>
                        {` (max. size: ${fileSizeLimit})`}
                      </form>
                    )}{' '}
                  </div>
                </div>
                {editable && (
                  <button
                    className="btn btn-primary"
                    onClick={() => history.push('/profile/edit')}
                  >
                    {t('common:Edit')}
                  </button>
                )}
                {isDeletable && (
                  <button
                    className="btn btn-danger"
                    onClick={() => displayModal(true)}
                  >
                    {t('user:Delete user account')}
                  </button>
                )}
                <button
                  className="btn btn-secondary"
                  onClick={() =>
                    pathname === '/profile' ? history.push('/') : history.go(-1)
                  }
                >
                  {t(
                    pathname === '/profile'
                      ? 'common:Back to home'
                      : 'common:Back'
                  )}
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default withTranslation()(
  connect(
    state => ({
      appConfig: state.application.config,
      pathname: state.router.location.pathname,
      message: state.message,
    }),
    dispatch => ({
      onDeletePicture: () => {
        dispatch(deletePicture())
      },
      onUploadPicture: event => {
        dispatch(uploadPicture(event))
      },
    })
  )(ProfileDetail)
)
