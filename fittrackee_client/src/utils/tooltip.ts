import { TStatisticsDatasetKeys } from '@/types/statistics'
import { formatDuration } from '@/utils/duration'

export const formatTooltipValue = (
  displayedData: TStatisticsDatasetKeys,
  value: number,
  formatWithUnits = true
): string => {
  return displayedData === 'total_duration'
    ? formatDuration(value, formatWithUnits)
    : displayedData === 'total_distance'
    ? value.toFixed(2) + ' km'
    : value.toString()
}
