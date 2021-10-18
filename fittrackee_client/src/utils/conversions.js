export const convert = (value, format) => {
  let ret = value
  if (format === 'mi') {
    ret = (ret * 0.62137119223733).toFixed(2)
  } else if (format === 'ft') {
    ret = (ret * 3.280839895).toFixed(2)
  }
  return parseFloat(ret)
}

export const convertBack = (value, format, direction = 'none') => {
  let ret = value
  if (direction === 'down') {
    if (format === 'mi') {
      ret = Math.floor(ret / 0.62137119223733)
    } else if (format === 'ft') {
      ret = Math.floor(ret / 3.280839895)
    }
  } else if (direction === 'up') {
    if (format === 'mi') {
      ret = Math.ceil(ret / 0.62137119223733)
    } else if (format === 'ft') {
      ret = Math.ceil(ret / 3.280839895)
    }
  } else {
    if (format === 'mi') {
      ret = (ret / 0.62137119223733).toFixed(2)
    } else if (format === 'ft') {
      ret = (ret / 3.280839895).toFixed(2)
    }
  }
  return parseFloat(ret)
}
