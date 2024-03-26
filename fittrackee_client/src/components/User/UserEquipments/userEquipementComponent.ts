import { useI18n } from 'vue-i18n'

import { getDuration } from '@/utils/duration'

export default function userEquipmentComponent() {
  const { t } = useI18n()
  function getTotalDuration(totalDuration: string) {
    if (totalDuration.match(/day/g)) {
      const durations = getDuration(totalDuration, t)
      return `${durations.days}, ${durations.duration}`
    }
    return totalDuration
  }

  return {
    getTotalDuration,
  }
}
