import hash from 'object-hash'
import React from 'react'
import { GeoJSON, Map, Marker, TileLayer } from 'react-leaflet'
import { connect } from 'react-redux'

import { getActivityGpx, getSegmentGpx } from '../../../actions/activities'
import { apiUrl } from '../../../utils'
import { getGeoJson } from '../../../utils/activities'

class ActivityMap extends React.Component {
  constructor(props, context) {
    super(props, context)
    this.state = {
      zoom: 13,
    }
  }

  componentDidMount() {
    if (this.props.dataType === 'activity') {
      this.props.loadActivityGpx(this.props.activity.id)
    } else {
      this.props.loadSegmentGpx(this.props.activity.id, this.props.segmentId)
    }
  }

  componentDidUpdate(prevProps) {
    if (
      (this.props.dataType === 'activity' &&
        prevProps.activity.id !== this.props.activity.id) ||
      (this.props.dataType === 'activity' && prevProps.dataType === 'segment')
    ) {
      this.props.loadActivityGpx(this.props.activity.id)
    }
    if (
      this.props.dataType === 'segment' &&
      prevProps.segmentId !== this.props.segmentId
    ) {
      this.props.loadSegmentGpx(this.props.activity.id, this.props.segmentId)
    }
  }

  componentWillUnmount() {
    this.props.loadActivityGpx(null)
  }

  render() {
    const { activity, coordinates, gpxContent } = this.props
    const { jsonData } = getGeoJson(gpxContent)
    const bounds = [
      [activity.bounds[0], activity.bounds[1]],
      [activity.bounds[2], activity.bounds[3]],
    ]

    return (
      <div>
        {jsonData && (
          <Map
            zoom={this.state.zoom}
            bounds={bounds}
            boundsOptions={{ padding: [10, 10] }}
          >
            <TileLayer
              // eslint-disable-next-line max-len
              attribution='&copy; <a href="http://www.thunderforest.com/">Thunderforest</a>, &copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
              url={`${apiUrl}activities/map_tile/{s}/{z}/{x}/{y}.png`}

            />
            <GeoJSON
              // hash as a key to force re-rendering
              key={hash(jsonData)}
              data={jsonData}
            />
            {coordinates.latitude && (
              <Marker
                position={[coordinates.latitude, coordinates.longitude]}
              />
            )}
          </Map>
        )}
      </div>
    )
  }
}

export default connect(
  state => ({
    gpxContent: state.gpx,
  }),
  dispatch => ({
    loadActivityGpx: activityId => {
      dispatch(getActivityGpx(activityId))
    },
    loadSegmentGpx: (activityId, segmentId) => {
      dispatch(getSegmentGpx(activityId, segmentId))
    },
  })
)(ActivityMap)
