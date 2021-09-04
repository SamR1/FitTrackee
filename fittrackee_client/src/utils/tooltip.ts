import { TDatasetKeys } from '@/types/statistics'
import { formatDuration } from '@/utils/duration'

export const formatTooltipValue = (
  displayedData: TDatasetKeys,
  value: number
): string => {
  return displayedData === 'total_duration'
    ? formatDuration(value, true)
    : displayedData === 'total_distance'
    ? value.toFixed(2) + ' km'
    : value.toString()
}
