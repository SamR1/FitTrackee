import React from 'react'

export default function ActivityNotes(props) {
  const { notes } = props
  return (
    <div className="card">
      <div className="card-body">
        Notes
        <div className="activity-notes">
          {notes ? notes : 'No notes'}
        </div>
      </div>
    </div>
  )
}
