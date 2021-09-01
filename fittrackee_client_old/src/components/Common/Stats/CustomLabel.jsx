import React from 'react'

import { formatValue } from '../../../utils/stats'

/**
 * @return {null}
 */
export default function CustomLabel(props) {
  const { displayedData, x, y, width, value } = props
  if (!value) {
    return null
  }
  const radius = 10
  const formattedValue = formatValue(displayedData, value)

  return (
    <g>
      <text
        x={x + width / 2}
        y={y - radius}
        fill="#666"
        fontSize="11"
        textAnchor="middle"
        dominantBaseline="middle"
      >
        {formattedValue}
      </text>
    </g>
  )
}
