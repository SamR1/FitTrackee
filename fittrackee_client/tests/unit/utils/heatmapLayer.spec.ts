import { CRS, latLng } from 'leaflet'
import { describe, it, expect } from 'vitest'

import type { IHeatmapCell } from '@/types/map'
import { drawCells, getMetersPerPixel } from '@/utils/heatmapLayer'

const getContext = () => {
  const calls: string[] = []
  const context = {
    fillStyle: '',
    beginPath: () => calls.push('beginPath'),
    rect: (x: number, y: number, w: number, h: number) =>
      calls.push(`rect ${x},${y} ${w}x${h}`),
    fill: () => calls.push(`fill ${context.fillStyle}`),
  }
  return { context, calls }
}

// one degree per pixel keeps the expected values readable
const project = (longitude: number, latitude: number): [number, number] => [
  longitude,
  -latitude,
]

const cell = (
  color: string,
  west: number,
  south: number,
  east: number,
  north: number
): IHeatmapCell => ({ color, west, south, east, north })

describe('drawCells', () => {
  it('draws nothing when there is no cell', () => {
    const { context, calls } = getContext()

    drawCells(context, [], project)

    expect(calls).toEqual([])
  })

  it('draws a cell from its bounds', () => {
    const { context, calls } = getContext()

    drawCells(context, [cell('#111111', 10, 20, 14, 26)], project)

    expect(calls).toEqual(['beginPath', 'rect 10,-26 4x6', 'fill #111111'])
  })

  it('gives a cell at least one pixel, to avoid seams', () => {
    const { context, calls } = getContext()

    drawCells(context, [cell('#111111', 10, 20, 10, 20)], project)

    expect(calls).toContain('rect 10,-20 1x1')
  })

  it('fills once per color, not once per cell', () => {
    const { context, calls } = getContext()

    drawCells(
      context,
      [
        cell('#aaaaaa', 0, 0, 1, 1),
        cell('#aaaaaa', 1, 0, 2, 1),
        cell('#aaaaaa', 2, 0, 3, 1),
        cell('#bbbbbb', 3, 0, 4, 1),
      ],
      project
    )

    expect(calls.filter((call) => call.startsWith('fill'))).toEqual([
      'fill #aaaaaa',
      'fill #bbbbbb',
    ])
    expect(calls.filter((call) => call === 'beginPath')).toHaveLength(2)
  })
})

describe('getMetersPerPixel', () => {
  // the API derives the cell size from the same world size and tile size
  const WORLD = 40075016.6855785
  const TILE = 256

  it.each([2, 8, 12, 16, 19])('matches the API scale at zoom %s', (zoom) => {
    const meters = getMetersPerPixel(CRS.EPSG3857, zoom, latLng(1.34, 103.82))

    expect(meters).toBeCloseTo(WORLD / (TILE * 2 ** zoom), 6)
  })

  it('does not depend on latitude', () => {
    expect(getMetersPerPixel(CRS.EPSG3857, 14, latLng(60, 10))).toBeCloseTo(
      getMetersPerPixel(CRS.EPSG3857, 14, latLng(-1, 103)),
      6
    )
  })
})
