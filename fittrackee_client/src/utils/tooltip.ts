import type { TStatisticsDatasetKeys } from '@/types/statistics'
import { formatDuration } from '@/utils/duration'
import { units } from '@/utils/units'

export const formatTooltipValue = (
  displayedData: TStatisticsDatasetKeys,
  value: number,
  useImperialUnits: boolean,
  formatWithUnits = true,
  unitFrom = 'km'
): string => {
  const unitTo = useImperialUnits ? units[unitFrom].defaultTarget : unitFrom
  switch (displayedData) {
    case 'average_speed':
      return `${value.toFixed(2)} ${unitTo}/h`
    case 'average_duration':
    case 'total_duration':
      return formatDuration(value, { formatWithUnits })
    case 'average_distance':
    case 'average_ascent':
    case 'average_descent':
    case 'total_distance':
    case 'total_ascent':
    case 'total_descent':
      return `${value.toFixed(2)} ${unitTo}`
    default:
      return value.toString()
  }
}
