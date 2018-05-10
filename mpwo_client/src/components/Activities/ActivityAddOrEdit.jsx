import React from 'react'
import { Helmet } from 'react-helmet'

import FormWithGpx from './ActivityForms/FormWithGpx'
import FormWithoutGpx from './ActivityForms/FormWithoutGpx'

export default class ActivityAddEdit extends React.Component {
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
    const { activity, message, sports } = this.props
    const { withGpx } = this.state
    return (
      <div>
        <Helmet>
          <title>mpwo - {activity
            ? 'Edit an activity'
            : 'Add an activity'}
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
                  {activity ? 'Edit an activity' : 'Add an activity'}
                </h2>
                <div className="card-body">
                  {activity ? (
                    activity.with_gpx ? (
                      'You can\'t modify this activity.' +
                        ' Please delete and re-import gpx file.'
                    ) : (
                    <FormWithoutGpx
                      activity={activity}
                      sports={sports}
                    />
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

