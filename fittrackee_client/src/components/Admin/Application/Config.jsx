import React from 'react'
import { Helmet } from 'react-helmet'

import Message from '../../Common/Message'
import { history } from '../../../index'
import { getFileSize } from '../../../utils'

export default function Config({ appConfig, message, t, updateIsInEdition }) {
  return (
    <div>
      <Helmet>
        <title>
          FitTrackee - {t('administration:Application configuration')}
        </title>
      </Helmet>
      <Message message={message} t={t} />
      <div className="container">
        <div className="row">
          <div className="col-md-12">
            <div className="card">
              <div className="card-header">
                {t('administration:Application configuration')}
              </div>
              <div className="card-body">
                <div className="row">
                  <div className="col">
                    <table className="table">
                      <tbody>
                        <tr>
                          <th scope="row">
                            {t(
                              // eslint-disable-next-line max-len
                              'administration:Max. number of active users (if 0, no limitation)'
                            )}
                            :
                          </th>
                          <td>{appConfig.max_users}</td>
                        </tr>
                        <tr>
                          <th scope="row">
                            {t('administration:Max. size of uploaded files')}:
                          </th>
                          <td>{getFileSize(appConfig.max_single_file_size)}</td>
                        </tr>
                        <tr>
                          <th scope="row">
                            {t('administration:Max. size of zip archive')}:
                          </th>
                          <td>{getFileSize(appConfig.max_zip_file_size)}</td>
                        </tr>
                        <tr>
                          <th scope="row">
                            {t('administration:Max. files of zip archive')}:
                          </th>
                          <td>{appConfig.gpx_limit_import}</td>
                        </tr>
                      </tbody>
                    </table>
                    <input
                      type="submit"
                      className="btn btn-primary btn-lg btn-block"
                      onClick={() => updateIsInEdition()}
                      value={t('common:Edit')}
                    />
                    <input
                      type="submit"
                      className="btn btn-secondary btn-lg btn-block"
                      onClick={() => history.push('/admin')}
                      value={t('common:Back')}
                    />
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
