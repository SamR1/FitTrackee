import React from 'react'
import { Map, TileLayer } from 'react-leaflet'

import { thunderforestApiKey } from '../../utils'

export default class ActivityMap extends React.Component {

  constructor(props, context) {
    super(props, context)
    this.state = {
    lat: 51.505,
    lng: -0.09,
    zoom: 13,
    }
  }

  render() {
    const position = [this.state.lat, this.state.lng]
    return (
      <Map center={position} zoom={this.state.zoom}>
        <TileLayer
          // eslint-disable-next-line max-len
          attribution='&copy; <a href="http://www.thunderforest.com/">Thunderforest</a>, &copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
          url="https://{s}.tile.thunderforest.com/outdoors/{z}/{x}/{y}.png"
          apikey={thunderforestApiKey}
        />
      </Map>
    )
  }
}
