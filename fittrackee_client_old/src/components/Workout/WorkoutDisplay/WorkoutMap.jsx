import React from 'react'
import { MapContainer } from 'react-leaflet'
import { connect } from 'react-redux'

import Map from './Map'
import { getSegmentGpx, getWorkoutGpx } from '../../../actions/workouts'
import { getGeoJson } from '../../../utils/workouts'

class WorkoutMap extends React.Component {
  constructor(props, context) {
    super(props, context)
    this.state = {
      zoom: 13,
    }
  }

  componentDidMount() {
    if (this.props.dataType === 'workout') {
      this.props.loadWorkoutGpx(this.props.workout.id)
    } else {
      this.props.loadSegmentGpx(this.props.workout.id, this.props.segmentId)
    }
  }

  componentDidUpdate(prevProps) {
    if (
      (this.props.dataType === 'workout' &&
        prevProps.workout.id !== this.props.workout.id) ||
      (this.props.dataType === 'workout' && prevProps.dataType === 'segment')
    ) {
      this.props.loadWorkoutGpx(this.props.workout.id)
    }
    if (
      this.props.dataType === 'segment' &&
      prevProps.segmentId !== this.props.segmentId
    ) {
      this.props.loadSegmentGpx(this.props.workout.id, this.props.segmentId)
    }
  }

  componentWillUnmount() {
    this.props.loadWorkoutGpx(null)
  }

  render() {
    const { coordinates, gpxContent, mapAttribution, workout } = this.props
    const { jsonData } = getGeoJson(gpxContent)
    const bounds = [
      [workout.bounds[0], workout.bounds[1]],
      [workout.bounds[2], workout.bounds[3]],
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
    loadWorkoutGpx: workoutId => {
      dispatch(getWorkoutGpx(workoutId))
    },
    loadSegmentGpx: (workoutId, segmentId) => {
      dispatch(getSegmentGpx(workoutId, segmentId))
    },
  })
)(WorkoutMap)
