import React from 'react'
import { Trans } from 'react-i18next'
import { connect } from 'react-redux'

import { setLoading } from '../../../actions/index'
import { addActivity, editActivity } from '../../../actions/activities'
import { history } from '../../../index'
import { fileSizeLimit, gpxLimit, zipSizeLimit } from '../../../utils'
import { translateSports } from '../../../utils/activities'

function FormWithGpx(props) {
  const { activity, loading, onAddActivity, onEditActivity, sports, t } = props
  const sportId = activity ? activity.sport_id : ''
  const translatedSports = translateSports(sports, t)
  // prettier-ignore
  const zipTooltip =
    `${t('activities:no folder inside')}, ${gpxLimit} ${
    t('activities:files max')}, ${t('activities:max size')}: ${zipSizeLimit}`
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
      {activity ? (
        <div className="form-group">
          <label>
            {t('activities:Title')}:
            <input
              name="title"
              defaultValue={activity ? activity.title : ''}
              disabled={loading}
              className="form-control input-lg"
            />
          </label>
        </div>
      ) : (
        <div className="form-group">
          <label>
            <Trans i18nKey="activities:gpxFile">
              <strong>gpx</strong> file
            </Trans>
            <sup>
              <i
                className="fa fa-question-circle"
                aria-hidden="true"
                data-toggle="tooltip"
                title={`${t('activities:max size')}: ${fileSizeLimit}`}
              />
            </sup>{' '}
            <Trans i18nKey="activities:zipFile">
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
          {t('activities:Notes')}:
          <textarea
            name="notes"
            defaultValue={activity ? activity.notes : ''}
            disabled={loading}
            className="form-control input-lg"
            maxLength="500"
          />
        </label>
      </div>
      {loading ? (
        <div className="loader" />
      ) : (
        <div>
          <input
            type="submit"
            className="btn btn-primary btn-lg btn-block"
            onClick={event =>
              activity ? onEditActivity(event, activity) : onAddActivity(event)
            }
            value={t('common:Submit')}
          />
          <input
            type="submit"
            className="btn btn-secondary btn-lg btn-block"
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
    loading: state.loading,
  }),
  dispatch => ({
    onAddActivity: e => {
      dispatch(setLoading(true))
      const form = new FormData()
      form.append('file', e.target.form.gpxFile.files[0])
      /* prettier-ignore */
      form.append(
        'data',
        `{"sport_id": ${e.target.form.sport.value
        }, "notes": "${e.target.form.notes.value}"}`
      )
      dispatch(addActivity(form))
    },
    onEditActivity: (e, activity) => {
      dispatch(
        editActivity({
          id: activity.id,
          notes: e.target.form.notes.value,
          sport_id: +e.target.form.sport.value,
          title: e.target.form.title.value,
        })
      )
    },
  })
)(FormWithGpx)
