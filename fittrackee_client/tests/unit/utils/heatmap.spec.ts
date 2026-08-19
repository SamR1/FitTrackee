import { describe, it, expect } from 'vitest'

import type { IHeatmapCells } from '@/types/map'
import {
  fromWebMercator,
  getColorScale,
  getHeatmapCells,
  getHeatmapLegend,
  getRampColor,
  getSmoothingPasses,
  heatmapColors,
  smoothCounts,
} from '@/utils/heatmap'

const cellSize = 9.554628535647035

const getCells = (cells: number[][], size = cellSize): IHeatmapCells => ({
  cells,
  cell_size: size,
})

describe('fromWebMercator', () => {
  it('matches the projection used by the API', () => {
    // values returned by PostGIS ST_Transform for 6.07367, 44.68095
    const [longitude, latitude] = fromWebMercator(
      676117.8516463819,
      5571432.665038707
    )

    expect(longitude).toBeCloseTo(6.07367, 6)
    expect(latitude).toBeCloseTo(44.68095, 6)
  })
})

describe('getHeatmapCells', () => {
  it('returns no cell when the size is unknown', () => {
    expect(getHeatmapCells(getCells([[1, 2, 1]], 0))).toEqual([])
  })

  it('places a cell at its indices, one cell size wide', () => {
    const [cell] = getHeatmapCells(getCells([[1000, 2000, 1]]))

    expect(cell.east).toBeGreaterThan(cell.west)
    expect(cell.north).toBeGreaterThan(cell.south)
    expect(fromWebMercator(1000 * cellSize, 2000 * cellSize)).toEqual([
      cell.west,
      cell.south,
    ])
  })

  it('colors each cell after its count', () => {
    const cells = getHeatmapCells(
      getCells([
        [0, 0, 1],
        [1, 0, 50],
      ])
    )

    expect(cells[0].color).toEqual(heatmapColors[0])
    expect(cells[1].color).toEqual(heatmapColors[heatmapColors.length - 1])
  })

  it('orders the cells from the least to the most travelled', () => {
    const cells = getHeatmapCells(
      getCells([
        [0, 0, 50],
        [1, 0, 1],
        [2, 0, 9],
      ])
    )

    // the ramp darkens, so the red channel decreases
    const reds = cells.map((cell) => parseInt(cell.color.slice(1, 3), 16))
    expect(reds).toEqual([...reds].sort((a, b) => b - a))
  })
})

describe('smoothCounts', () => {
  it('returns the counts unchanged without a pass', () => {
    const counts = smoothCounts(
      [
        [0, 0, 3],
        [1, 0, 5],
      ],
      0
    )

    expect(counts.get('0:0')).toEqual(3)
    expect(counts.get('1:0')).toEqual(5)
  })

  it('keeps the level of a cell surrounded by cells of the same count', () => {
    const cells: number[][] = []
    for (let i = -1; i <= 1; i++) {
      for (let j = -1; j <= 1; j++) {
        cells.push([i, j, 10])
      }
    }

    const counts = smoothCounts(cells, 1)

    expect(counts.get('0:0')).toEqual(10)
  })

  it('fades a cell that has no neighbour', () => {
    const counts = smoothCounts([[0, 0, 16]], 1)

    // only its own weight, 4 of 16, is left
    expect(counts.get('0:0')).toEqual(4)
  })

  it('pulls a cell towards a busier neighbour, not towards zero', () => {
    const alone = smoothCounts([[0, 0, 10]], 1).get('0:0') as number
    const beside = smoothCounts(
      [
        [0, 0, 10],
        [1, 0, 100],
      ],
      1
    ).get('0:0') as number

    expect(beside).toBeGreaterThan(alone)
  })

  it('spreads by one cell per pass', () => {
    expect(smoothCounts([[0, 0, 10]], 1).has('2:0')).toBe(false)
    expect(smoothCounts([[0, 0, 10]], 2).has('2:0')).toBe(true)
  })

  it('drops the cells that faded away', () => {
    const counts = smoothCounts([[0, 0, 0.1]], 2)

    expect([...counts.values()].every((count) => count >= 0.05)).toBe(true)
  })
})

describe('getSmoothingPasses', () => {
  it.each([
    [1, 2],
    [2, 2],
    [3, 1],
    [5, 1],
    // when zoomed in past the stored resolution, the detail is worth more
    // than a glow
    [6, 0],
    [8, 0],
  ])('smooths cells of %s px with %s passes', (cellPixels, expected) => {
    expect(getSmoothingPasses(cellPixels)).toEqual(expected)
  })

  it('returns no pass for an unknown cell size', () => {
    expect(getSmoothingPasses(0)).toEqual(0)
  })
})

describe('getRampColor', () => {
  it('returns the ends of the ramp', () => {
    expect(getRampColor(0)).toEqual(heatmapColors[0])
    expect(getRampColor(1)).toEqual(heatmapColors[heatmapColors.length - 1])
  })

  it('clamps positions outside the ramp', () => {
    expect(getRampColor(-1)).toEqual(heatmapColors[0])
    expect(getRampColor(2)).toEqual(heatmapColors[heatmapColors.length - 1])
  })

  it('interpolates between two colors of the ramp', () => {
    // halfway between the first two anchors
    const color = getRampColor(0.5 / (heatmapColors.length - 1))

    expect(color).not.toEqual(heatmapColors[0])
    expect(color).not.toEqual(heatmapColors[1])
    const red = parseInt(color.slice(1, 3), 16)
    expect(red).toBeGreaterThan(parseInt(heatmapColors[1].slice(1, 3), 16))
    expect(red).toBeLessThan(parseInt(heatmapColors[0].slice(1, 3), 16))
  })
})

describe('getColorScale', () => {
  it('returns the lightest color when there is no cell', () => {
    expect(getColorScale([])(1)).toEqual(heatmapColors[0])
  })

  it('gives the least and most travelled the ends of the ramp', () => {
    const counts = [1, 2, 3, 40, 500]
    const scale = getColorScale(counts)

    expect(scale(1)).toEqual(heatmapColors[0])
    expect(scale(500)).toEqual(heatmapColors[heatmapColors.length - 1])
  })

  it('follows the distribution, not the values', () => {
    // one huge outlier must not push everything else to the lightest color
    const scale = getColorScale([1, 2, 3, 4, 10000])

    expect(scale(3)).not.toEqual(heatmapColors[0])
  })

  it('never goes down as the count goes up', () => {
    const counts = [1, 1, 2, 5, 9, 30, 100]
    const scale = getColorScale(counts)

    const positions = counts.map((count) =>
      parseInt(scale(count).slice(1, 3), 16)
    )
    // the ramp darkens, so the red channel decreases
    expect(positions).toEqual([...positions].sort((a, b) => b - a))
  })
})

describe('getHeatmapLegend', () => {
  it('returns nothing without counts', () => {
    expect(getHeatmapLegend([])).toEqual([])
  })

  it('samples the ramp with increasing counts', () => {
    const legend = getHeatmapLegend([1, 1, 2, 3, 8, 20, 90])

    expect(legend.length).toBeGreaterThan(1)
    expect(legend[0].color).toEqual(heatmapColors[0])
    const values = legend.map((sample) => Number(sample.label))
    expect(values).toEqual([...values].sort((a, b) => a - b))
  })

  it('drops duplicated samples when counts are alike', () => {
    expect(getHeatmapLegend([4, 4, 4, 4])).toHaveLength(1)
  })
})
