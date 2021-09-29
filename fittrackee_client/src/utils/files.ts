const suffixes = ['bytes', 'KB', 'MB', 'GB', 'TB']

export const getReadableFileSize = (
  fileSize: number,
  asText = true
): string | Record<string, string> => {
  const i = Math.floor(Math.log(fileSize) / Math.log(1024))
  if (!fileSize) {
    return asText ? '0 bytes' : { size: '0', suffix: 'bytes' }
  }
  const size = (fileSize / Math.pow(1024, i)).toFixed(1)
  const suffix = suffixes[i]
  return asText ? `${size}${suffix}` : { size, suffix }
}
