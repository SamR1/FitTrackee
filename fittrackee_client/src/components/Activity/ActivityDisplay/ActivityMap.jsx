import React from 'react'
import { MapContainer } from 'react-leaflet'
import { connect } from 'react-redux'

import Map from './Map'
import { getActivityGpx, getSegmentGpx } from '../../../actions/activities'
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
    const { activity, coordinates, gpxContent, mapAttribution } = this.props
    const { jsonData } = getGeoJson(gpxContent)
    const bounds = [
      [activity.bounds[0], activity.bounds[1]],
      [activity.bounds[2], activity.bounds[3]],
    ]

    return (
      <div>
        {jsonData && (
          <MapContainer
            zoom={this.state.zoom}
            bounds={bounds}
            boundsOptions={{ padding: [10, 10] }}
          >
            <Map
              bounds={bounds}
              coordinates={coordinates}
              jsonData={jsonData}
              mapAttribution={mapAttribution}
            />
          </MapContainer>
        )}
      </div>
    )
  }
}

export default connect(
  state => ({
    gpxContent: state.gpx,
    mapAttribution: state.application.config.map_attribution,
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
