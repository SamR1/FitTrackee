import { TStatisticsDatasetKeys } from '@/types/statistics'
import { formatDuration } from '@/utils/duration'
import { units } from '@/utils/units'

export const formatTooltipValue = (
  displayedData: TStatisticsDatasetKeys,
  value: number,
  useImperialUnits: boolean,
  formatWithUnits = true
): string => {
  const unitFrom = 'km'
  const unitTo = useImperialUnits ? units[unitFrom].defaultTarget : unitFrom
  switch (displayedData) {
    case 'total_duration':
      return formatDuration(value, formatWithUnits)
    case 'total_distance':
      return `${value.toFixed(2)} ${unitTo}`
    case 'total_ascent':
    case 'total_descent':
      return `${(value / 1000).toFixed(2)} ${unitTo}`
    default:
      return value.toString()
  }
}
