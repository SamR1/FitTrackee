import React from 'react'

export default function ActivitiesList (props) {
  const { sports } = props
  return (
    <div className="card">
      <div className="card-body activity-filter">
        <form onSubmit={event => event.preventDefault()}>
          <div className="form-group">
            <label>
              From:
              <input
                name="start"
                className="form-control col-md"
                type="date"
              />
            </label>
            <label>
              To:
              <input
                name="end"
                className="form-control col-md"
                type="date"
              />
            </label>
          </div>
          <div className="form-group">
            <label>
              Sport:
              <select
                className="form-control input-lg"
                name="sport_id"
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
              Distance (km):
              <div className="container">
                <div className="row">
                  <div className="col-5">
                    <input
                      name="distance-from"
                      className="form-control"
                      min={0}
                      step="1"
                      type="number"
                    />
                  </div>
                  <div className="col-2 align-middle text-center">to</div>
                  <div className="col-5">
                    <input
                      name="distance-to"
                      className="form-control"
                      min={0}
                      step="1"
                      type="number"
                    />
                  </div>
                </div>
              </div>
            </label>
          </div>
          <div className="form-group">
            <label>
              Duration:
              <div className="container">
                <div className="row">
                  <div className="col-5">
                    <input
                      name="duration-from"
                      className="form-control"
                      pattern="^([0-9]*[0-9]):([0-5][0-9])$"
                      placeholder="hh:mm"
                      type="text"
                    />
                  </div>
                  <div className="col-2 align-middle text-center">to</div>
                  <div className="col-5">
                    <input
                      name="duration-to"
                      className="form-control"
                      pattern="^([0-9]*[0-9]):([0-5][0-9])$"
                      placeholder="hh:mm"
                      type="text"
                    />
                  </div>
                </div>
              </div>
            </label>
          </div>
          <div className="form-group">
            <label>
              Average speed (km/h):
              <div className="container">
                <div className="row">
                  <div className="col-5">
                    <input
                      name="speed-from"
                      className="form-control"
                      min={0}
                      step="1"
                      type="number"
                    />
                  </div>
                  <div className="col-2 align-middle text-center">to</div>
                  <div className="col-5">
                    <input
                      name="speed-to"
                      className="form-control"
                      min={0}
                      step="1"
                      type="number"
                    />
                  </div>
                </div>
              </div>
            </label>
          </div>
          <input
            type="submit"
            className="btn btn-primary btn-lg btn-block"
            value="Filter"
          />
        </form>
      </div>
    </div>
  )
}
