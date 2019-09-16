import React from 'react'
import { Helmet } from 'react-helmet'
import { withTranslation } from 'react-i18next'
import { connect } from 'react-redux'

import FormWithGpx from './ActivityForms/FormWithGpx'
import FormWithoutGpx from './ActivityForms/FormWithoutGpx'

class ActivityAddEdit extends React.Component {
  constructor(props, context) {
    super(props, context)
    this.state = {
      withGpx: true,
    }
  }

  handleRadioChange(changeEvent) {
    this.setState({
      withGpx:
        changeEvent.target.name === 'withGpx'
          ? changeEvent.target.value
          : !changeEvent.target.value,
    })
  }

  render() {
    const { activity, loading, message, sports, t } = this.props
    const { withGpx } = this.state
    return (
      <div>
        <Helmet>
          <title>
            FitTrackee -{' '}
            {activity
              ? t('activities:Edit a workout')
              : t('activities:Add a workout')}
          </title>
        </Helmet>
        <br />
        <br />
        {message && <code>{t(`messages:${message}`)}</code>}
        <div className="container">
          <div className="row">
            <div className="col-md-2" />
            <div className="col-md-8">
              <div className="card add-activity">
                <h2 className="card-header text-center">
                  {activity
                    ? t('activities:Edit a workout')
                    : t('activities:Add a workout')}
                </h2>
                <div className="card-body">
                  {activity ? (
                    activity.with_gpx ? (
                      <FormWithGpx activity={activity} sports={sports} t={t} />
                    ) : (
                      <FormWithoutGpx
                        activity={activity}
                        sports={sports}
                        t={t}
                      />
                    )
                  ) : (
                    <div>
                      <form>
                        <div className="form-group row">
                          <div className="col">
                            <label className="radioLabel">
                              <input
                                className="add-activity-radio"
                                type="radio"
                                name="withGpx"
                                disabled={loading}
                                checked={withGpx}
                                onChange={event =>
                                  this.handleRadioChange(event)
                                }
                              />
                              {t('activities:with gpx file')}
                            </label>
                          </div>
                          <div className="col">
                            <label className="radioLabel">
                              <input
                                className="add-activity-radio"
                                type="radio"
                                name="withoutGpx"
                                disabled={loading}
                                checked={!withGpx}
                                onChange={event =>
                                  this.handleRadioChange(event)
                                }
                              />
                              {t('activities:without gpx file')}
                            </label>
                          </div>
                        </div>
                      </form>
                      {withGpx ? (
                        <FormWithGpx sports={sports} t={t} />
                      ) : (
                        <FormWithoutGpx sports={sports} t={t} />
                      )}
                    </div>
                  )}
                </div>
              </div>
            </div>
            <div className="col-md-2" />
          </div>
        </div>
      </div>
    )
  }
}

export default withTranslation()(
  connect(state => ({
    loading: state.loading,
  }))(ActivityAddEdit)
)
