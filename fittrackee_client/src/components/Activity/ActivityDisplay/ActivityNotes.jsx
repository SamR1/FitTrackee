import React from 'react'

export default function ActivityNotes(props) {
  const { notes } = props
  return (
    <div className="row">
      <div className="col">
        <div className="card activity-card">
          <div className="card-body">
            Notes
            <div className="activity-notes">
              {notes ? notes : 'No notes'}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
