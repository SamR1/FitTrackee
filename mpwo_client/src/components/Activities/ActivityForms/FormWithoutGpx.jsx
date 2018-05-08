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
          <input
            name="activity_date"
            className="form-control input-lg"
            type="date"
          />
        </label>
      </div>
      <div className="form-group">
        <label>
          Duration:
          <input
            name="duration"
            className="form-control input-lg"
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
      const data = [].slice
        .call(e.target.form.elements)
        .reduce(function(map, obj) {
          if (obj.name) {
            if (obj.name === 'duration' || obj.name === 'distance') {
              map[obj.name] = +obj.value
            } else {
              map[obj.name] = obj.value
            }
          }
          return map
        }, {})
      dispatch(addActivityWithoutGpx(data))
    },
  })
)(FormWithoutGpx)
