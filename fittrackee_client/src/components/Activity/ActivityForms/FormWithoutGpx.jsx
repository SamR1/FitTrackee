import React from 'react'
import { connect } from 'react-redux'

import {
  addActivityWithoutGpx,
  editActivity,
} from '../../../actions/activities'
import { history } from '../../../index'
import { formatActivityDate, translateSports } from '../../../utils/activities'

function FormWithoutGpx(props) {
  const { activity, onAddOrEdit, sports, t } = props
  const translatedSports = translateSports(sports, t, true)
  let activityDate,
    activityTime,
    sportId = ''
  if (activity) {
    const activityDateTime = formatActivityDate(
      activity.activity_date,
      'yyyy-MM-dd'
    )
    activityDate = activityDateTime.activity_date
    activityTime = activityDateTime.activity_time
    sportId = activity.sport_id
  }

  return (
    <form onSubmit={event => event.preventDefault()}>
      <div className="form-group">
        <label>
          {t('activities:Title')}:
          <input
            name="title"
            defaultValue={activity ? activity.title : ''}
            className="form-control input-lg"
          />
        </label>
      </div>
      <div className="form-group">
        <label>
          {t('common:Sport')}:
          <select
            className="form-control input-lg"
            defaultValue={sportId}
            name="sport_id"
            required
          >
            <option value="" />
            {translatedSports.map(sport => (
              <option key={sport.id} value={sport.id}>
                {sport.label}
              </option>
            ))}
          </select>
        </label>
      </div>
      <div className="form-group">
        <label>
          {t('activities:Activity Date')}:
          <div className="container">
            <div className="row">
              <input
                name="activity_date"
                defaultValue={activityDate}
                className="form-control col-md"
                required
                type="date"
              />
              <input
                name="activity_time"
                defaultValue={activityTime}
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
          {t('activities:Duration')}:
          <input
            name="duration"
            defaultValue={activity ? activity.duration : ''}
            className="form-control col-xs-4"
            pattern="^([0-9]*[0-9]):([0-5][0-9]):([0-5][0-9])$"
            placeholder="hh:mm:ss"
            required
            type="text"
          />
        </label>
      </div>
      <div className="form-group">
        <label>
          {t('activities:Distance')} (km):
          <input
            name="distance"
            defaultValue={activity ? activity.distance : ''}
            className="form-control input-lg"
            min={0}
            required
            step="0.001"
            type="number"
          />
        </label>
      </div>
      <div className="form-group">
        <label>
          {t('activities:Notes')}:
          <textarea
            name="notes"
            defaultValue={activity ? activity.notes : ''}
            className="form-control input-lg"
            maxLength="500"
          />
        </label>
      </div>
      <input
        type="submit"
        className="btn btn-primary btn-lg btn-block"
        onClick={event => onAddOrEdit(event, activity)}
        value={t('common:Submit')}
      />
      <input
        type="submit"
        className="btn btn-secondary btn-lg btn-block"
        onClick={() => history.push('/')}
        value={t('common:Cancel')}
      />
    </form>
  )
}

export default connect(
  () => ({}),
  dispatch => ({
    onAddOrEdit: (e, activity) => {
      const d = e.target.form.duration.value.split(':')
      const duration = +d[0] * 60 * 60 + +d[1] * 60 + +d[2]

      /* prettier-ignore */
      const activityDate = `${e.target.form.activity_date.value
        } ${ e.target.form.activity_time.value}`

      const data = {
        activity_date: activityDate,
        distance: +e.target.form.distance.value,
        duration,
        notes: e.target.form.notes.value,
        sport_id: +e.target.form.sport_id.value,
        title: e.target.form.title.value,
      }
      if (activity) {
        data.id = activity.id
        dispatch(editActivity(data))
      } else {
        dispatch(addActivityWithoutGpx(data))
      }
    },
  })
)(FormWithoutGpx)
