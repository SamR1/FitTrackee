import React from 'react'
import { Helmet } from 'react-helmet'
import { connect } from 'react-redux'

import { addActivity } from '../../actions/activities'
import { getData } from '../../actions/index'
import { history } from '../../index'


class AddActivity extends React.Component {
  componentDidMount() {
      this.props.loadSports()
  }

  render() {
    const { message, onAddSport, sports } = this.props

    return (
      <div>
        <Helmet>
          <title>mpwo - Add an activity</title>
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
                  Add a sport
                </h2>
                <div className="card-body">
                  <form
                    encType="multipart/form-data"
                    method="post"
                    onSubmit={event => event.preventDefault()}
                  >
                    <div className="form-group">
                      <label>
                        Sport:
                        <select
                          className="form-control input-lg"
                          name="sport"
                          required
                        >
                          <option value="" />
                          {sports.map(sport => (
                            <option key={sport.id} value={sport.id}>
                              {sport.label}
                            </option>
                          ))}
                        </select>
                      </label>
                    </div>
                    <div className="form-group">
                      <label>
                        GPX file:
                        <input
                          accept=".gpx"
                          className="form-control input-lg"
                          name="gpxFile"
                          required
                          type="file"
                        />
                      </label>
                    </div>
                    <input
                      type="submit"
                      className="btn btn-primary btn-lg btn-block"
                      onClick={event => onAddSport(event)}
                      value="Submit"
                    />
                    <input
                      type="submit"
                      className="btn btn-secondary btn-lg btn-block"
                      onClick={() => history.go(-1)}
                      value="Cancel"
                    />
                  </form>
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
    message: state.message,
    sports: state.sports.data,
    user: state.user,
  }),
  dispatch => ({
    loadSports: () => {
      dispatch(getData('sports'))
    },
    onAddSport: event => {
      const form = new FormData()
      form.append('file', event.target.form.gpxFile.files[0])
      form.append(
        'data', `{"sport_id": ${event.target.form.sport.value}}`
      )
      dispatch(addActivity(form))
    },
  })
)(AddActivity)
