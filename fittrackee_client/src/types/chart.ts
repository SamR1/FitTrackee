export interface IChartDataset {
  label: string
  backgroundColor: string[]
  borderColor?: string[]
  borderWidth?: number
  fill?: boolean
  data: (number | null)[]
  yAxisID?: string
  type?: string
  spanGaps?: boolean
}
