import React from 'react'
import { Link } from 'react-router-dom'

export default function ActivitySegments(props) {
  const { segments, t } = props
  return (
    <div className="row">
      <div className="col">
        <div className="card activity-card">
          <div className="card-body">
            {t('activities:Segments')}
            <div className="activity-segments">
              <ul>
                {segments.map((segment, index) => (
                  <li
                    className="activity-segments-list"
                    // eslint-disable-next-line react/no-array-index-key
                    key={`segment-${index}`}
                  >
                    <Link
                      to={`/activities/${segment.activity_id}/segment/${
                        index + 1
                      }`}
                    >
                      {t('activities:segment')} {index + 1}
                    </Link>{' '}
                    ({t('activities:distance')}: {segment.distance} km,{' '}
                    {t('activities:duration')}: {segment.duration})
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
