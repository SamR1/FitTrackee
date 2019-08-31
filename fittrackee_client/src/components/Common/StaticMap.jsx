import React from 'react'

import { apiUrl } from '../../utils'

export default class StaticMap extends React.PureComponent {
  render() {
    const { activity } = this.props
    return (
      <>
        <img
          className="activity-map"
          src={`${apiUrl}activities/map/${activity.map}?${Date.now()}`}
          alt="activity map"
        />
        <div className="map-attribution text-right">
          <span className="map-attribution-text">©</span>
          <a
            className="map-attribution-text"
            href="http://www.openstreetmap.org/copyright"
            target="_blank"
            rel="noopener noreferrer"
          >
            OpenStreetMap
          </a>
        </div>
      </>
    )
  }
}
