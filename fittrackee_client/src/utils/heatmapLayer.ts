import { DomUtil, Layer, Util, type CRS, type LatLng, type Map } from 'leaflet'

import type { IHeatmapCell, IHeatmapCells } from '@/types/map.ts'
import { getHeatmapCells, getSmoothingPasses } from '@/utils/heatmap.ts'

/**
 * Meters of Web Mercator per pixel, taken from the map projection so that the
 * cell size the API returns can be turned into a size on screen.
 */
export function getMetersPerPixel(
  crs: CRS,
  zoom: number,
  center: LatLng
): number {
  const point = crs.latLngToPoint(center, zoom)
  const eastOfPixel = crs.pointToLatLng(point.add([1, 0]), zoom)
  return crs.project(eastOfPixel).x - crs.project(center).x
}

export function drawCells(
  context: Pick<CanvasRenderingContext2D, 'beginPath' | 'rect' | 'fill'> & {
    fillStyle: string | CanvasGradient | CanvasPattern
  },
  cells: IHeatmapCell[],
  project: (longitude: number, latitude: number) => [number, number]
): void {
  let currentColor = ''
  cells.forEach((cell) => {
    if (cell.color !== currentColor) {
      if (currentColor) {
        context.fill()
      }
      context.beginPath()
      context.fillStyle = cell.color
      currentColor = cell.color
    }
    const [left, top] = project(cell.west, cell.north)
    const [right, bottom] = project(cell.east, cell.south)
    // cells are drawn side by side: rounding up avoids seams between them
    context.rect(
      left,
      top,
      Math.max(right - left, 1),
      Math.max(bottom - top, 1)
    )
  })
  if (currentColor) {
    context.fill()
  }
}

/**
 * A viewport holds thousands of cells: one Leaflet layer per cell would spend
 * more time on layer bookkeeping than on drawing, so they share a single
 * canvas covering the viewport.
 */
const HeatmapLayer = Layer.extend({
  options: {
    opacity: 0.85,
    // the counts are already smoothed over the neighbouring cells: this only
    // softens what is left of the cell edges
    blurRatio: 0.25,
  },

  initialize(collection: IHeatmapCells, options?: object) {
    this._collection = collection
    Util.setOptions(this, options)
  },

  setCells(collection: IHeatmapCells) {
    this._collection = collection
    this._redraw()
    return this
  },

  /**
   * Size of a cell on screen, from the map projection rather than from the
   * API constants, and how much the counts are smoothed for it.
   */
  _getCells(): IHeatmapCell[] {
    const map = this._map as Map
    const zoom = map.getZoom()
    if (
      this._cells &&
      this._zoom === zoom &&
      this._built === this._collection
    ) {
      return this._cells
    }
    const metersPerPixel = getMetersPerPixel(
      map.options.crs!,
      zoom,
      map.getCenter()
    )
    const cellPixels = metersPerPixel
      ? this._collection.cell_size / metersPerPixel
      : 0
    this._cells = getHeatmapCells(
      this._collection,
      getSmoothingPasses(cellPixels)
    )
    this._zoom = zoom
    this._built = this._collection
    return this._cells
  },

  onAdd(map: Map) {
    this._map = map
    this._canvas = DomUtil.create(
      'canvas',
      'leaflet-layer'
    ) as HTMLCanvasElement
    DomUtil.addClass(this._canvas, 'leaflet-zoom-hide')
    map.getPanes().overlayPane.appendChild(this._canvas)
    map.on('moveend zoomend resize', this._reset, this)
    this._reset()
  },

  onRemove(map: Map) {
    map.off('moveend zoomend resize', this._reset, this)
    this._canvas.remove()
  },

  _reset() {
    const map = this._map as Map
    const size = map.getSize()
    const ratio = window.devicePixelRatio || 1
    this._canvas.width = size.x * ratio
    this._canvas.height = size.y * ratio
    this._canvas.style.width = `${size.x}px`
    this._canvas.style.height = `${size.y}px`
    DomUtil.setPosition(this._canvas, map.containerPointToLayerPoint([0, 0]))
    this._redraw()
  },

  _redraw() {
    if (!this._map || !this._canvas) {
      return
    }
    const map = this._map as Map
    const context = this._canvas.getContext('2d')
    if (!context) {
      return
    }
    const ratio = window.devicePixelRatio || 1
    context.setTransform(ratio, 0, 0, ratio, 0, 0)
    context.clearRect(0, 0, this._canvas.width, this._canvas.height)
    context.globalAlpha = this.options.opacity

    const project = (longitude: number, latitude: number): [number, number] => {
      const { x, y } = map.latLngToContainerPoint([latitude, longitude])
      return [x, y]
    }
    const cells = this._getCells()
    const blur = this._getBlur(cells, project)
    if (!blur) {
      drawCells(context, cells, project)
      return
    }
    // the cells are drawn apart, then blurred in one pass: blurring each color
    // on the shared canvas would blur it over the previous ones too
    const layer = document.createElement('canvas')
    layer.width = this._canvas.width
    layer.height = this._canvas.height
    const layerContext = layer.getContext('2d')
    if (!layerContext) {
      drawCells(context, cells, project)
      return
    }
    layerContext.setTransform(ratio, 0, 0, ratio, 0, 0)
    drawCells(layerContext, cells, project)
    context.setTransform(1, 0, 0, 1, 0, 0)
    context.filter = `blur(${blur * ratio}px)`
    context.drawImage(layer, 0, 0)
    context.filter = 'none'
  },

  _getBlur(
    cells: IHeatmapCell[],
    project: (longitude: number, latitude: number) => [number, number]
  ) {
    const context = this._canvas.getContext('2d')
    const cell = cells[0]
    // older Safari has no canvas filter: the cells stay square there
    if (!cell || !context || !('filter' in context)) {
      return 0
    }
    const [left] = project(cell.west, cell.north)
    const [right] = project(cell.east, cell.south)
    return Math.abs(right - left) * this.options.blurRatio
  },
})

export function createHeatmapLayer(
  collection: IHeatmapCells,
  options?: object
) {
  return new (HeatmapLayer as unknown as {
    new (
      collection: IHeatmapCells,
      options?: object
    ): Layer & { setCells: (collection: IHeatmapCells) => void }
  })(collection, options)
}

export type THeatmapLayer = ReturnType<typeof createHeatmapLayer>
