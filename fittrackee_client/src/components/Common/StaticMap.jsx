import React from 'react'

import { apiUrl } from '../../utils'

export default class StaticMap extends React.PureComponent {
  render() {
    const { display, workout } = this.props

    return (
      <div className={`workout-map${display === 'list' ? '-list' : ''}`}>
        <img
          src={`${apiUrl}workouts/map/${workout.map}?${Date.now()}`}
          alt="workout map"
        />
        <div className={`map-attribution${display === 'list' ? '-list' : ''}`}>
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
      </div>
    )
  }
}
