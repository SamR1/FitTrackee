import React from 'react'

import { apiUrl } from '../../utils'

export default class StaticMap extends React.PureComponent {
  render() {
    const { activity, display } = this.props
    const attributionStyle =
      display === 'list' ? 'map-attribution-list' : 'map-attribution text-right'

    return (
      <>
        <img
          className="activity-map"
          src={`${apiUrl}activities/map/${activity.map}?${Date.now()}`}
          alt="activity map"
        />
        <div className={attributionStyle}>
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
