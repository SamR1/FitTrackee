import React from 'react'
import { withTranslation } from 'react-i18next'
import { connect } from 'react-redux'

import { getAppData } from '../../actions/application'

class AdminStats extends React.Component {
  componentDidMount() {
    this.props.loadAppStats()
  }

  render() {
    const { appStats, t } = this.props
    return (
      <div className="row">
        <div className="col-md-4">
          <div className="card activity-card">
            <div className="card-body row">
              <div className="col-3">
                <i className="fa fa-users fa-3x fa-color" />
              </div>
              <div className="col-9 text-right">
                <div className="huge">
                  {appStats.users ? appStats.users : 0}
                </div>
                <div>{`${
                  appStats.users === 1
                    ? t('administration:user')
                    : t('administration:users')
                }`}</div>
              </div>
            </div>
          </div>
        </div>
        <div className="col-md-4">
          <div className="card activity-card">
            <div className="card-body row">
              <div className="col-3">
                <i className="fa fa-tags fa-3x fa-color" />
              </div>
              <div className="col-9 text-right">
                <div className="huge">
                  {appStats.sports ? appStats.sports : 0}
                </div>
                <div>{`${
                  appStats.sports === 1 ? t('common:sport') : t('common:sports')
                }`}</div>
              </div>
            </div>
          </div>
        </div>
        <div className="col-md-4">
          <div className="card activity-card">
            <div className="card-body row">
              <div className="col-3">
                <i className="fa fa-calendar fa-3x fa-color" />
              </div>
              <div className="col-9 text-right">
                <div className="huge">
                  {appStats.activities ? appStats.activities : 0}
                </div>
                <div>{`${
                  appStats.activities === 1
                    ? t('common:workout')
                    : t('common:workouts')
                }`}</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    )
  }
}

export default withTranslation()(
  connect(
    state => ({
      appStats: state.application.statistics,
    }),
    dispatch => ({
      loadAppStats: () => {
        dispatch(getAppData('stats/all'))
      },
    })
  )(AdminStats)
)
