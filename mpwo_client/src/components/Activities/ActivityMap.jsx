import React from 'react'
import { GeoJSON, Map, TileLayer } from 'react-leaflet'
import { connect } from 'react-redux'

import { getActivityGpx } from '../../actions/activities'
import { getGeoJson, thunderforestApiKey } from '../../utils'

class ActivityMap extends React.Component {

  constructor(props, context) {
    super(props, context)
    this.state = {
      zoom: 13,
    }
  }

  componentDidMount() {
    this.props.loadActivityGpx(this.props.activity.id)
  }

  componentWillUnmount() {
    this.props.loadActivityGpx(null)
  }

  render() {
    const { gpxContent } = this.props
    const { jsonData, bounds } = getGeoJson(gpxContent)

    return (
      <div>
        {jsonData && (
          <Map
            zoom={this.state.zoom}
            bounds={bounds}
            boundsOptions={{ padding: [50, 50] }}
          >
            <TileLayer
              // eslint-disable-next-line max-len
              attribution='&copy; <a href="http://www.thunderforest.com/">Thunderforest</a>, &copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
              // eslint-disable-next-line max-len
              url={`https://{s}.tile.thunderforest.com/outdoors/{z}/{x}/{y}.png?apikey=${thunderforestApiKey}`}
            />
            <GeoJSON data={jsonData} />
          </Map>
        )}
      </div>

    )
  }
}

export default connect(
  state => ({
    gpxContent: state.gpx
  }),
  dispatch => ({
    loadActivityGpx: activityId => {
      dispatch(getActivityGpx(activityId))
    },
  })
)(ActivityMap)
