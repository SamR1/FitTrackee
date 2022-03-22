export const formatDuration = (
  totalSeconds: number,
  formatWithUnits = false
): string => {
  let days = '0'
  if (formatWithUnits) {
    days = String(Math.floor(totalSeconds / 86400))
    totalSeconds %= 86400
  }
  const hours = String(Math.floor(totalSeconds / 3600)).padStart(2, '0')
  totalSeconds %= 3600
  const minutes = String(Math.floor(totalSeconds / 60)).padStart(2, '0')
  const seconds = String(totalSeconds % 60).padStart(2, '0')
  if (formatWithUnits) {
    return `${days === '0' ? '' : `${days}d `}${
      hours === '00' ? '' : `${hours}h `
    }${minutes}m ${seconds}s`
  }
  return `${hours === '00' ? '' : `${hours}:`}${minutes}:${seconds}`
}
