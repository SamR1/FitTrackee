import React from 'react'
import { Link } from 'react-router-dom'

import { getDateWithTZ } from '../../../utils'
import { formatActivityDate } from '../../../utils/activities'

export default function ActivityCardHeader(props) {
  const {
    activity,
    dataType,
    displayModal,
    segmentId,
    sport,
    t,
    title,
    user,
  } = props
  const activityDate = activity
    ? formatActivityDate(getDateWithTZ(activity.activity_date, user.timezone))
    : null

  const previousUrl =
    dataType === 'segment' && segmentId !== 1
      ? `/activities/${activity.id}/segment/${segmentId - 1}`
      : dataType === 'activity' && activity.previous_activity
      ? `/activities/${activity.previous_activity}`
      : null
  const nextUrl =
    dataType === 'segment' && segmentId < activity.segments.length
      ? `/activities/${activity.id}/segment/${segmentId + 1}`
      : dataType === 'activity' && activity.next_activity
      ? `/activities/${activity.next_activity}`
      : null

  return (
    <div className="container">
      <div className="row">
        <div className="col-auto">
          {previousUrl ? (
            <Link className="unlink" to={previousUrl}>
              <i
                className="fa fa-chevron-left"
                aria-hidden="true"
                title={t(`activities:See previous ${dataType}`)}
              />
            </Link>
          ) : (
            <i
              className="fa fa-chevron-left inactive-link"
              aria-hidden="true"
              title={t(`activities:No previous ${dataType}`)}
            />
          )}
        </div>
        <div className="col-auto col-activity-logo">
          <img className="sport-img-medium" src={sport.img} alt="sport logo" />
        </div>
        <div className="col">
          {dataType === 'activity' ? (
            <>
              {title}{' '}
              <Link className="unlink" to={`/activities/${activity.id}/edit`}>
                <i
                  className="fa fa-edit custom-fa"
                  aria-hidden="true"
                  title={t('activities:Edit activity')}
                />
              </Link>
              <i
                className="fa fa-trash custom-fa"
                aria-hidden="true"
                onClick={() => displayModal(true)}
                title={t('activities:Delete activity')}
              />
            </>
          ) : (
            <>
              {/* prettier-ignore */}
              <Link
                to={`/activities/${activity.id}`}
              >
                {title}
              </Link>{' '}
              - {t('activities:segment')} {segmentId}
            </>
          )}
          <br />
          {activityDate && (
            <span className="activity-date">
              {`${activityDate.activity_date} - ${activityDate.activity_time}`}
            </span>
          )}
        </div>
        <div className="col-auto">
          {nextUrl ? (
            <Link className="unlink" to={nextUrl}>
              <i
                className="fa fa-chevron-right"
                aria-hidden="true"
                title={t(`activities:See next ${dataType}`)}
              />
            </Link>
          ) : (
            <i
              className="fa fa-chevron-right inactive-link"
              aria-hidden="true"
              title={t(`activities:No next ${dataType}`)}
            />
          )}
        </div>
      </div>
    </div>
  )
}
