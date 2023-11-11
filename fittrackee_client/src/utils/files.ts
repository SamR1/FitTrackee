import type { IFileSize } from '@/types/application'

const suffixes = ['bytes', 'KB', 'MB', 'GB', 'TB']

export const getReadableFileSize = (fileSize: number): IFileSize => {
  if (!fileSize) {
    return { size: '0', suffix: 'bytes' }
  }
  const i = Math.floor(Math.log(fileSize) / Math.log(1024))
  const size = (fileSize / Math.pow(1024, i)).toFixed(1)
  const suffix = suffixes[i]
  return { size, suffix }
}

export const getReadableFileSizeAsText = (fileSize: number): string => {
  if (!fileSize) {
    return '0 bytes'
  }
  const readableFileSize = getReadableFileSize(fileSize)
  return `${readableFileSize.size}${readableFileSize.suffix}`
}

export const getFileSizeInMB = (fileSize: number): number => {
  const value = fileSize / 1048576
  return (!fileSize && 0) || +value.toFixed(2)
}
