import React from 'react'

import { formatValue } from '../../../utils/stats'

export default function CustomLabel (props) {
  const { displayedData, x, y, width, value } = props
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
