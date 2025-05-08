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
