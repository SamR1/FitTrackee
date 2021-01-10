import React from 'react'
import { GeoJSON, Marker, TileLayer, useMap } from 'react-leaflet'
import hash from 'object-hash'

import { apiUrl } from '../../../utils'

export default function Map({ bounds, coordinates, jsonData, mapAttribution }) {
  const map = useMap()
  map.fitBounds(bounds)
  return (
    <>
      <TileLayer
        // eslint-disable-next-line max-len
        attribution={mapAttribution}
        url={`${apiUrl}workouts/map_tile/{s}/{z}/{x}/{y}.png`}
      />
      <GeoJSON
        // hash as a key to force re-rendering
        key={hash(jsonData)}
        data={jsonData}
      />
      {coordinates.latitude && (
        <Marker position={[coordinates.latitude, coordinates.longitude]} />
      )}
    </>
  )
}
