const directions = [
  'N',
  'NNE',
  'NE',
  'ENE',
  'E',
  'ESE',
  'SE',
  'SSE',
  'S',
  'SSW',
  'SW',
  'WSW',
  'W',
  'WNW',
  'NW',
  'NNW',
]

export const convertDegreeToDirection = (angle: number): string => {
  const value = Math.floor(angle / 22.5 + 0.5)
  return directions[value % 16]
}
