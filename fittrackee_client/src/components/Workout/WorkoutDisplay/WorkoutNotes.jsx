import React from 'react'

export default function WorkoutNotes(props) {
  const { notes, t } = props
  return (
    <div className="row">
      <div className="col">
        <div className="card workout-card">
          <div className="card-body">
            Notes
            <div className="workout-notes">
              {notes ? notes : t('workouts:No notes')}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
