import React from 'react'
import { Helmet } from 'react-helmet'
import { withTranslation } from 'react-i18next'
import { connect } from 'react-redux'

import FormWithGpx from './WorkoutForms/FormWithGpx'
import FormWithoutGpx from './WorkoutForms/FormWithoutGpx'
import Message from '../Common/Message'

class WorkoutAddEdit extends React.Component {
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
    const { loading, message, sports, t, workout } = this.props
    const { withGpx } = this.state
    return (
      <div>
        <Helmet>
          <title>
            FitTrackee -{' '}
            {workout
              ? t('workouts:Edit a workout')
              : t('workouts:Add a workout')}
          </title>
        </Helmet>
        <br />
        <br />
        <Message message={message} t={t} />
        <div className="container">
          <div className="row">
            <div className="col-md-2" />
            <div className="col-md-8">
              <div className="card add-workout">
                <h2 className="card-header text-center">
                  {workout
                    ? t('workouts:Edit a workout')
                    : t('workouts:Add a workout')}
                </h2>
                <div className="card-body">
                  {workout ? (
                    workout.with_gpx ? (
                      <FormWithGpx workout={workout} sports={sports} t={t} />
                    ) : (
                      <FormWithoutGpx workout={workout} sports={sports} t={t} />
                    )
                  ) : (
                    <div>
                      <form>
                        <div className="form-group row">
                          <div className="col">
                            <label className="radioLabel">
                              <input
                                className="add-workout-radio"
                                type="radio"
                                name="withGpx"
                                disabled={loading}
                                checked={withGpx}
                                onChange={event =>
                                  this.handleRadioChange(event)
                                }
                              />
                              {t('workouts:with gpx file')}
                            </label>
                          </div>
                          <div className="col">
                            <label className="radioLabel">
                              <input
                                className="add-workout-radio"
                                type="radio"
                                name="withoutGpx"
                                disabled={loading}
                                checked={!withGpx}
                                onChange={event =>
                                  this.handleRadioChange(event)
                                }
                              />
                              {t('workouts:without gpx file')}
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
  }))(WorkoutAddEdit)
)
