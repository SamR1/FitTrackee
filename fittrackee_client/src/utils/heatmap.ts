import type { IHeatmapCell, IHeatmapCells } from '@/types/map.ts'

export const heatmapColors = [
  '#b7d3f6',
  '#86b6ef',
  '#3987e5',
  '#1c5cab',
  '#0d366b',
]

const EARTH_RADIUS = 6378137

export function fromWebMercator(x: number, y: number): [number, number] {
  return [
    (x / EARTH_RADIUS) * (180 / Math.PI),
    (2 * Math.atan(Math.exp(y / EARTH_RADIUS)) - Math.PI / 2) * (180 / Math.PI),
  ]
}

// the ramp is interpolated between these colors, and quantized to that many
// shades: enough for a smooth gradient, few enough for the canvas to fill once
// per shade
const RAMP_SHADES = 64

function interpolateChannel(from: number, to: number, ratio: number): number {
  return Math.round(from + (to - from) * ratio)
}

/**
 * Color of the ramp at the given position, 0 being the least travelled.
 */
export function getRampColor(position: number): string {
  const clamped = Math.max(0, Math.min(1, position))
  const scaled = clamped * (heatmapColors.length - 1)
  const index = Math.min(Math.floor(scaled), heatmapColors.length - 2)
  const ratio = scaled - index
  const from = heatmapColors[index]
  const to = heatmapColors[index + 1]
  const channels = [1, 3, 5].map((offset) =>
    interpolateChannel(
      parseInt(from.slice(offset, offset + 2), 16),
      parseInt(to.slice(offset, offset + 2), 16),
      ratio
    )
  )
  return `#${channels
    .map((channel) => channel.toString(16).padStart(2, '0'))
    .join('')}`
}

/**
 * Map the counts to the ramp through their cumulative distribution, so that
 * the colors follow how the counts are actually spread: they are strongly
 * skewed, most cells being crossed a handful of times while a few hubs
 * concentrate hundreds of workouts, and a linear scale would leave nearly
 * every cell in the first color.
 */
export function getColorScale(counts: number[]): (count: number) => string {
  if (counts.length === 0) {
    return () => heatmapColors[0]
  }
  const sorted = [...counts].sort((a, b) => a - b)
  const shades = [...Array(RAMP_SHADES + 1).keys()].map((shade) =>
    getRampColor(shade / RAMP_SHADES)
  )
  return (count: number) => {
    // share of the cells this one is more travelled than
    let low = 0
    let high = sorted.length
    while (low < high) {
      const middle = (low + high) >> 1
      if (sorted[middle] < count) {
        low = middle + 1
      } else {
        high = middle
      }
    }
    const position = sorted.length > 1 ? low / (sorted.length - 1) : 0
    return shades[Math.round(Math.max(0, Math.min(1, position)) * RAMP_SHADES)]
  }
}

/**
 * A few samples of the ramp, labelled with the count each one starts at.
 */
export function getHeatmapLegend(
  counts: number[]
): { color: string; label: string }[] {
  if (counts.length === 0) {
    return []
  }
  const sorted = [...counts].sort((a, b) => a - b)
  const samples = heatmapColors.map((_color, index) => {
    const position = index / (heatmapColors.length - 1)
    return {
      color: getRampColor(position),
      from: Math.round(sorted[Math.floor(position * (sorted.length - 1))]),
    }
  })
  return samples
    .filter(
      (sample, index) => index === 0 || sample.from > samples[index - 1].from
    )
    .map(({ color, from }) => ({ color, label: `${from}` }))
}

// how far the counts spread, in pixels: the passes are derived from it, so
// that the glow keeps the same width whatever the size of the cells on screen
const SPREAD_PIXELS = 5
// each pass grows the cells to smooth, and sub-pixel cells need little help
// to stop looking like a grid
const MAX_SMOOTHING_PASSES = 2

/**
 * Number of smoothing passes for cells of the given size on screen. Large
 * cells, when zoomed in past the stored resolution, are left alone: their
 * detail is worth more than a glow.
 */
export function getSmoothingPasses(cellPixels: number): number {
  if (cellPixels <= 0) {
    return 0
  }
  return Math.min(Math.floor(SPREAD_PIXELS / cellPixels), MAX_SMOOTHING_PASSES)
}

function getCellKey(i: number, j: number): string {
  return `${i}:${j}`
}

// weights of a cell and its neighbours; a missing neighbour counts as zero,
// so a cell keeps its level inside a cluster and only fades on a real edge
const NEIGHBOURS: [number, number, number][] = [
  [-1, -1, 1],
  [0, -1, 2],
  [1, -1, 1],
  [-1, 0, 2],
  [0, 0, 4],
  [1, 0, 2],
  [-1, 1, 1],
  [0, 1, 2],
  [1, 1, 1],
]
const WEIGHTS = NEIGHBOURS.reduce((total, [, , weight]) => total + weight, 0)
// below this a cell is not worth drawing, and stops the smoothing from
// spreading a faint halo further at each pass
const MIN_COUNT = 0.05

/**
 * Spread the counts over the neighbouring cells, so that the heatmap reads as
 * tracks instead of squares: a cell next to a busier one is pulled towards its
 * level, rather than towards the background as a plain blur would do.
 */
export function smoothCounts(
  cells: number[][],
  passes: number
): Map<string, number> {
  let counts = new Map<string, number>(
    cells.map(([i, j, count]) => [getCellKey(i, j), count])
  )
  for (let pass = 0; pass < passes; pass++) {
    const smoothed = new Map<string, number>()
    // the counts spread by one cell per pass, so the neighbours join in
    const keys = new Set<string>()
    counts.forEach((_count, key) => {
      const [i, j] = key.split(':').map(Number)
      NEIGHBOURS.forEach(([di, dj]) => keys.add(getCellKey(i + di, j + dj)))
    })
    keys.forEach((key) => {
      const [i, j] = key.split(':').map(Number)
      const total = NEIGHBOURS.reduce(
        (sum, [di, dj, weight]) =>
          sum + weight * (counts.get(getCellKey(i + di, j + dj)) ?? 0),
        0
      )
      const count = total / WEIGHTS
      if (count >= MIN_COUNT) {
        smoothed.set(key, count)
      }
    })
    counts = smoothed
  }
  return counts
}

/**
 * Turn the cell indices returned by the API into their bounds and color. The
 * grid origin is the Web Mercator one, so a cell only depends on its indices
 * and on the size the API merged them to.
 */
export function getHeatmapCells(
  collection: IHeatmapCells,
  smoothingPasses = 0
): IHeatmapCell[] {
  const { cell_size: cellSize } = collection
  if (cellSize <= 0) {
    return []
  }
  const counts = smoothCounts(collection.cells, smoothingPasses)
  const getColor = getColorScale([...counts.values()])
  // the scale grows with the count, so ordering the cells by count groups the
  // shades together for the canvas, and draws the most travelled ones on top
  return [...counts]
    .sort(([, a], [, b]) => a - b)
    .map(([key, count]) => {
      const [i, j] = key.split(':').map(Number)
      const [west, south] = fromWebMercator(i * cellSize, j * cellSize)
      const [east, north] = fromWebMercator(
        (i + 1) * cellSize,
        (j + 1) * cellSize
      )
      return { color: getColor(count), west, south, east, north }
    })
}
