import React from 'react'
import { connect } from 'react-redux'

import { addActivityWithoutGpx } from '../../../actions/activities'
import { history } from '../../../index'


function FormWithoutGpx (props) {
  const { onAddSport, sports } = props
  return (
    <form
      onSubmit={event => event.preventDefault()}
    >
      <div className="form-group">
        <label>
          Sport:
          <select
            className="form-control input-lg"
            name="sport_id"
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
          Activity Date:
          <div className="container">
            <div className="row">
              <input
                name="activity_date"
                className="form-control col-md"
                required
                type="date"
              />
              <input
                name="activity_time"
                className="form-control col-md"
                required
                type="time"
              />
            </div>
          </div>
        </label>
      </div>
      <div className="form-group">
        <label>
          Duration:
            <input
              name="duration"
              className="form-control col-xs-4"
              pattern="([0-2][0-3]):([0-5][0-9]):([0-5][0-9])"
              placeholder="hh:mm:ss"
              required
              type="text"
            />
        </label>
      </div>
      <div className="form-group">
        <label>
          Distance (km):
          <input
            name="distance"
            className="form-control input-lg"
            min={0}
            required
            type="number"
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
    onAddSport: e => {
      const d = e.target.form.duration.value.split(':')
      const duration = +d[0] * 60 * 60 + +d[1] * 60 + +d[2]

      const activityDate = `${e.target.form.activity_date.value
        } ${ e.target.form.activity_time.value}`

      const data = {
        activity_date: activityDate,
        distance: +e.target.form.distance.value,
        duration,
        sport_id: +e.target.form.sport_id.value,
      }
      dispatch(addActivityWithoutGpx(data))
    },
  })
)(FormWithoutGpx)
