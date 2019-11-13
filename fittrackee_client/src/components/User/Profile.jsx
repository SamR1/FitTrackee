import { format } from 'date-fns'
import React from 'react'
import { Helmet } from 'react-helmet'
import { withTranslation } from 'react-i18next'
import { connect } from 'react-redux'
import { Link } from 'react-router-dom'

import Message from '../Common/Message'
import { deletePicture, uploadPicture } from '../../actions/user'
import { apiUrl, getFileSize } from '../../utils'

function Profile({
  appConfig,
  message,
  onDeletePicture,
  onUploadPicture,
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
                {user.username}{' '}
                <Link
                  to={{
                    pathname: '/profile/edit',
                  }}
                >
                  <i className="fa fa-pencil-square-o" aria-hidden="true" />
                </Link>
              </div>
              <div className="card-body">
                <div className="row">
                  <div className="col-md-8">
                    <p>
                      {t('user:Email')}: {user.email}
                    </p>
                    <p>
                      {t('user:Registration Date')}: {createdAt}
                    </p>
                    <p>
                      {t('user:First Name')}: {user.first_name}
                    </p>
                    <p>
                      {t('user:Last Name')}: {user.last_name}
                    </p>
                    <p>
                      {t('user:Birth Date')}: {birthDate}
                    </p>
                    <p>
                      {t('user:Location')}: {user.location}
                    </p>
                    <p>
                      {t('user:Bio')}: {user.bio}
                    </p>
                    <p>
                      {t('user:Language')}: {user.language}
                    </p>
                    <p>
                      {t('user:Timezone')}: {user.timezone}
                    </p>
                    <p>
                      {t('user:First day of week')}:{' '}
                      {user.weekm ? t('user:Monday') : t('user:Sunday')}
                    </p>
                  </div>
                  <div className="col-md-4">
                    {user.picture === true && (
                      <div>
                        <img
                          alt="Profile"
                          src={
                            `${apiUrl}users/${user.id}/picture` +
                            `?${Date.now()}`
                          }
                          className="img-fluid App-profile-img-small"
                        />
                        <br />
                        <button type="submit" onClick={() => onDeletePicture()}>
                          {t('user:Delete picture')}
                        </button>
                        <br />
                        <br />
                      </div>
                    )}
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
                  </div>
                </div>
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
      message: state.message,
      user: state.user,
    }),
    dispatch => ({
      onDeletePicture: () => {
        dispatch(deletePicture())
      },
      onUploadPicture: event => {
        dispatch(uploadPicture(event))
      },
    })
  )(Profile)
)
