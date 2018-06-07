import React from 'react'
import { Helmet } from 'react-helmet'
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

  handleRadioChange (changeEvent) {
    this.setState({
      withGpx:
        changeEvent.target.name === 'withGpx'
          ? changeEvent.target.value : !changeEvent.target.value
    })
  }

  render() {
    const { activity, loading, message, sports } = this.props
    const { withGpx } = this.state
    return (
      <div>
        <Helmet>
          <title>FitTrackee - {activity
            ? 'Edit a workout'
            : 'Add a workout'}
            </title>
        </Helmet>
        <br /><br />
        {message && (
          <code>{message}</code>
        )}
        <div className="container">
          <div className="row">
            <div className="col-md-2" />
            <div className="col-md-8">
              <div className="card add-activity">
                <h2 className="card-header text-center">
                  {activity ? 'Edit a workout' : 'Add a workout'}
                </h2>
                <div className="card-body">
                  {activity ? (
                    activity.with_gpx ? (
                      <FormWithGpx activity={activity} sports={sports} />
                    ) : (
                      <FormWithoutGpx activity={activity} sports={sports} />
                    )
                  ) : (
                    <div>
                      <form>
                        <div className="form-group row">
                          <div className="col">
                            <label className="radioLabel">
                            <input
                              type="radio"
                              name="withGpx"
                              disabled={loading}
                              checked={withGpx}
                              onChange={event => this.handleRadioChange(event)}
                            />
                              with gpx file
                            </label>
                          </div>
                          <div className="col">
                            <label className="radioLabel">
                            <input
                              type="radio"
                              name="withoutGpx"
                              disabled={loading}
                              checked={!withGpx}
                              onChange={event => this.handleRadioChange(event)}
                            />
                              without gpx file
                            </label>
                          </div>
                        </div>
                      </form>
                      {withGpx ? (
                        <FormWithGpx sports={sports} />
                      ) : (
                        <FormWithoutGpx sports={sports} />
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

export default connect(
  state => ({
    loading: state.loading
  }),
)(ActivityAddEdit)
