import { TStatisticsDatasetKeys } from '@/types/statistics'
import { formatDuration } from '@/utils/duration'

export const formatTooltipValue = (
  displayedData: TStatisticsDatasetKeys,
  value: number,
  formatWithUnits = true
): string => {
  switch (displayedData) {
    case 'total_duration':
      return formatDuration(value, formatWithUnits)
    case 'total_distance':
      return value.toFixed(2) + ' km'
    case 'total_ascent':
    case 'total_descent':
      return (value / 1000).toFixed(2) + ' km'
    default:
      return value.toString()
  }
}
