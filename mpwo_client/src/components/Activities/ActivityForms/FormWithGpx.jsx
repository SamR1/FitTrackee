import React from 'react'
import { connect } from 'react-redux'

import { addActivity } from '../../../actions/activities'
import { history } from '../../../index'


function FormWithGpx (props) {
  const { onAddSport, sports } = props
  return (
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
  )
}

export default connect(
  () => ({ }),
  dispatch => ({
    onAddSport: event => {
      const form = new FormData()
      form.append('file', event.target.form.gpxFile.files[0])
      form.append(
        'data', `{"sport_id": ${event.target.form.sport.value}}`
      )
      dispatch(addActivity(form))
    },
  })
)(FormWithGpx)
