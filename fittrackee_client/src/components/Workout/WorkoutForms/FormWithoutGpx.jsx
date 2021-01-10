import React from 'react'
import { connect } from 'react-redux'

import { addWorkoutWithoutGpx, editWorkout } from '../../../actions/workouts'
import { history } from '../../../index'
import { getDateWithTZ } from '../../../utils'
import { formatWorkoutDate, translateSports } from '../../../utils/workouts'

function FormWithoutGpx(props) {
  const { onAddOrEdit, sports, t, user, workout } = props
  const translatedSports = translateSports(sports, t, true)
  let workoutDate,
    workoutTime,
    sportId = ''
  if (workout) {
    const workoutDateTime = formatWorkoutDate(
      getDateWithTZ(workout.workout_date, user.timezone),
      'yyyy-MM-dd'
    )
    workoutDate = workoutDateTime.workout_date
    workoutTime = workoutDateTime.workout_time
    sportId = workout.sport_id
  }

  return (
    <form onSubmit={event => event.preventDefault()}>
      <div className="form-group">
        <label>
          {t('workouts:Title')}:
          <input
            name="title"
            defaultValue={workout ? workout.title : ''}
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
          {t('workouts:Workout Date')}:
          <div className="container">
            <div className="row">
              <input
                name="workout_date"
                defaultValue={workoutDate}
                className="form-control col-md"
                required
                type="date"
              />
              <input
                name="workout_time"
                defaultValue={workoutTime}
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
          {t('workouts:Duration')}:
          <input
            name="duration"
            defaultValue={workout ? workout.duration : ''}
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
          {t('workouts:Distance')} (km):
          <input
            name="distance"
            defaultValue={workout ? workout.distance : ''}
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
          {t('workouts:Notes')}:
          <textarea
            name="notes"
            defaultValue={workout ? workout.notes : ''}
            className="form-control input-lg"
            maxLength="500"
          />
        </label>
      </div>
      <input
        type="submit"
        className="btn btn-primary"
        onClick={event => onAddOrEdit(event, workout)}
        value={t('common:Submit')}
      />
      <input
        type="submit"
        className="btn btn-secondary"
        onClick={() => history.push('/')}
        value={t('common:Cancel')}
      />
    </form>
  )
}

export default connect(
  state => ({
    user: state.user,
  }),
  dispatch => ({
    onAddOrEdit: (e, workout) => {
      const d = e.target.form.duration.value.split(':')
      const duration = +d[0] * 60 * 60 + +d[1] * 60 + +d[2]

      /* prettier-ignore */
      const workoutDate = `${e.target.form.workout_date.value
        } ${ e.target.form.workout_time.value}`

      const data = {
        workout_date: workoutDate,
        distance: +e.target.form.distance.value,
        duration,
        notes: e.target.form.notes.value,
        sport_id: +e.target.form.sport_id.value,
        title: e.target.form.title.value,
      }
      if (workout) {
        data.id = workout.id
        dispatch(editWorkout(data))
      } else {
        dispatch(addWorkoutWithoutGpx(data))
      }
    },
  })
)(FormWithoutGpx)
