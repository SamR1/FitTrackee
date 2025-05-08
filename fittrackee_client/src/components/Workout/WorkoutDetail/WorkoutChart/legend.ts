import { Chart } from 'chart.js'
import type { LegendItem } from 'chart.js'

const getOrCreateLegendList = (id: string): HTMLUListElement => {
  const legendContainer = document.getElementById(id)
  if (legendContainer) {
    let listContainer = legendContainer.querySelector('ul')
    if (!listContainer) {
      listContainer = document.createElement('ul')
      legendContainer.appendChild(listContainer)
    }
    return listContainer
  }
  throw new Error('No legend container')
}

export const htmlLegendPlugin = {
  id: 'htmlLegend',
  afterUpdate(
    chart: Chart,
    args: Record<string, unknown>,
    options: Record<string, string>
  ): void {
    const ul = getOrCreateLegendList(options.containerID)
    while (ul.firstChild) {
      ul.firstChild.remove()
    }

    const legendItems = chart.options.plugins?.legend?.labels?.generateLabels
      ? chart.options.plugins?.legend?.labels?.generateLabels(chart)
      : []

    legendItems.forEach((item: LegendItem) => {
      const li = document.createElement('li')
      li.onclick = (e) => {
        e.preventDefault()
        if (item.datasetIndex !== undefined) {
          chart.setDatasetVisibility(
            item.datasetIndex,
            !chart.isDatasetVisible(item.datasetIndex)
          )
          chart.update()
        }
      }

      const checkBox = document.createElement('input')
      if (checkBox) {
        checkBox.type = 'checkbox'
        checkBox.id = item.text
        checkBox.checked = !item.hidden
      }

      const label = document.createElement('label')
      label.htmlFor = checkBox.id
      const labeltext = document.createTextNode(item.text)
      label.appendChild(labeltext)

      const boxSpan = document.createElement('span')
      if (boxSpan) {
        boxSpan.style.background = String(item.fillStyle)
        boxSpan.style.borderColor = String(item.strokeStyle)
      }

      label.appendChild(boxSpan)
      li.appendChild(checkBox)
      li.appendChild(label)
      ul.appendChild(li)
    })
  },
}
