export interface IChartDataset {
  backgroundColor: string[]
  borderColor?: string[]
  borderWidth?: number
  data: (number | null)[]
  fill?: boolean
  id?: string
  label: string
  spanGaps?: boolean
  type?: string
  yAxisID?: string
}

export interface IHoverPoint {
  dataIndex: number
  datasetIndex: number
  datasetLabel: string
  x: number
  y: number
}
