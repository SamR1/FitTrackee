import React from 'react'
import { Trans } from 'react-i18next'
import { connect } from 'react-redux'

import { setLoading } from '../../../actions/index'
import { addWorkout, editWorkout } from '../../../actions/workouts'
import { history } from '../../../index'
import { getFileSize } from '../../../utils'
import { translateSports } from '../../../utils/workouts'
import CustomTextArea from '../../Common/CustomTextArea'

function FormWithGpx(props) {
  const {
    appConfig,
    loading,
    onAddWorkout,
    onEditWorkout,
    sports,
    t,
    workout,
  } = props
  const sportId = workout ? workout.sport_id : ''
  const translatedSports = translateSports(sports, t, true)
  const zipTooltip = `${t('workouts:no folder inside')}, ${
    appConfig.gpx_limit_import
  } ${t('workouts:files max')}, ${t('workouts:max size')}: ${getFileSize(
    appConfig.max_zip_file_size
  )}`
  const fileSizeLimit = getFileSize(appConfig.max_single_file_size)
  return (
    <form
      encType="multipart/form-data"
      method="post"
      onSubmit={event => event.preventDefault()}
    >
      <div className="form-group">
        <label>
          {t('common:Sport')}:
          <select
            className="form-control input-lg"
            defaultValue={sportId}
            disabled={loading}
            name="sport"
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
      {workout ? (
        <div className="form-group">
          <label>
            {t('workouts:Title')}:
            <input
              name="title"
              defaultValue={workout ? workout.title : ''}
              disabled={loading}
              className="form-control input-lg"
            />
          </label>
        </div>
      ) : (
        <div className="form-group">
          <label>
            <Trans i18nKey="workouts:gpxFile">
              <strong>gpx</strong> file
            </Trans>
            <sup>
              <i
                className="fa fa-question-circle"
                aria-hidden="true"
                data-toggle="tooltip"
                title={`${t('workouts:max size')}: ${fileSizeLimit}`}
              />
            </sup>{' '}
            <Trans i18nKey="workouts:zipFile">
              or <strong> zip</strong> file containing <strong>gpx </strong>
              files
            </Trans>
            <sup>
              <i
                className="fa fa-question-circle"
                aria-hidden="true"
                data-toggle="tooltip"
                data-placement="top"
                title={zipTooltip}
              />
            </sup>{' '}
            :
            <input
              accept=".gpx, .zip"
              className="form-control form-control-file gpx-file"
              disabled={loading}
              name="gpxFile"
              required
              type="file"
            />
          </label>
        </div>
      )}
      <div className="form-group">
        <label>
          {t('workouts:Notes')}:
          <CustomTextArea
            charLimit={500}
            defaultValue={workout ? workout.notes : ''}
            loading={loading}
            name="notes"
          />
        </label>
      </div>
      {loading ? (
        <div className="loader" />
      ) : (
        <div>
          <input
            type="submit"
            className="btn btn-primary"
            onClick={event =>
              workout ? onEditWorkout(event, workout) : onAddWorkout(event)
            }
            value={t('common:Submit')}
          />
          <input
            type="submit"
            className="btn btn-secondary"
            onClick={() => history.push('/')}
            value={t('common:Cancel')}
          />
        </div>
      )}
    </form>
  )
}

export default connect(
  state => ({
    appConfig: state.application.config,
    loading: state.loading,
  }),
  dispatch => ({
    onAddWorkout: e => {
      dispatch(setLoading(true))
      const form = new FormData()
      form.append('file', e.target.form.gpxFile.files[0])
      /* prettier-ignore */
      form.append(
        'data',
        `{"sport_id": ${e.target.form.sport.value
        }, "notes": "${e.target.form.notes.value}"}`
      )
      dispatch(addWorkout(form))
    },
    onEditWorkout: (e, workout) => {
      dispatch(
        editWorkout({
          id: workout.id,
          notes: e.target.form.notes.value,
          sport_id: +e.target.form.sport.value,
          title: e.target.form.title.value,
        })
      )
    },
  })
)(FormWithGpx)
