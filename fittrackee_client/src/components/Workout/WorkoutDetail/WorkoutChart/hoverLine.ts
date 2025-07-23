import type { Chart } from 'chart.js'

export const verticalHoverLine = {
  id: 'verticalHoverLine',
  beforeDatasetDraw(chart: Chart): boolean | void {
    const {
      ctx,
      chartArea: { top, bottom },
    } = chart
    ctx.save()

    chart.getDatasetMeta(0).data.forEach((dataPoint) => {
      if (dataPoint.active) {
        ctx.beginPath()
        ctx.strokeStyle = 'gray'
        ctx.moveTo(dataPoint.x, top)
        ctx.lineTo(dataPoint.x, bottom)
        ctx.stroke()
      }
    })
  },
}
