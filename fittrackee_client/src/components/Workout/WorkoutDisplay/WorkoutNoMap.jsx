import React from 'react'

export default function WorkoutNoMap(props) {
  const { t } = props
  return (
    <div className="workout-no-map text-center">{t('workouts:No Map')}</div>
  )
}
