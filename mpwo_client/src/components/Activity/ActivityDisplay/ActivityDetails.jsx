import React from 'react'

export default function ActivityDetails(props) {
  const { activity } = props
  const withPauses = activity.pauses !== '0:00:00' && activity.pauses !== null
  const recordLDexists = activity.records.find(r => r.record_type === 'LD')
  return (
    <div>
      <p>
        <i
          className="fa fa-clock-o custom-fa"
          aria-hidden="true"
        />
        Duration: {activity.duration}
        {withPauses && (
          <span>
            {' '}
            (pauses: {activity.pauses})
            <br />
            Moving duration: {activity.moving}
          </span>
        )}
        {recordLDexists && (
          <sup>
            <i
              className="fa fa-trophy custom-fa"
              aria-hidden="true"
            />
          </sup>
        )}
      </p>
      <p>
        <i
          className="fa fa-road custom-fa"
          aria-hidden="true"
        />
        Distance: {activity.distance} km
        {activity.records.find(r => r.record_type === 'FD'
        ) && (
          <sup>
            <i
              className="fa fa-trophy custom-fa"
              aria-hidden="true"
            />
          </sup>
        )}
      </p>
      <p>
        <i
          className="fa fa-tachometer custom-fa"
          aria-hidden="true"
        />
        Average speed: {activity.ave_speed} km/h
        {activity.records.find(r => r.record_type === 'AS'
        ) && (
          <sup>
            <i
              className="fa fa-trophy custom-fa"
              aria-hidden="true"
            />
          </sup>
        )}
        <br />
        Max speed : {activity.max_speed} km/h
        {activity.records.find(r => r.record_type === 'MS'
        ) && (
          <sup>
            <i
              className="fa fa-trophy custom-fa"
              aria-hidden="true"
            />
          </sup>
        )}
      </p>
      {activity.min_alt && activity.max_alt && (
        <p>
          <i className="fi-mountains custom-fa" />
          Min altitude: {activity.min_alt}m
          <br />
          Max altitude: {activity.max_alt}m
        </p>
      )}
      {activity.ascent && activity.descent && (
        <p>
          <i className="fa fa-location-arrow custom-fa" />
          Ascent: {activity.ascent}m
          <br />
          Descent: {activity.descent}m
        </p>
      )}
    </div>
  )
}
