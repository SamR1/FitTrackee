import React from 'react'


export default function UserStatistics (props) {
  const { user } = props
  return (
    <div className="row">
      <div className="col">
        <div className="card activity-card">
          <div className="card-body row">
            <div className="col-3">
              <i className="fa fa-calendar fa-3x fa-color" />
            </div>
            <div className="col-9 text-right">
              <div className="huge">{user.nbActivities}</div>
              <div>{user.nbActivities === 1 ? 'activity' : 'activities'}</div>
            </div>
          </div>
        </div>
      </div>
      <div className="col">
        <div className="card activity-card">
          <div className="card-body row">
            <div className="col-3">
              <i className="fa fa-road fa-3x fa-color" />
            </div>
            <div className="col-9 text-right">
              <div className="huge">
                {Math.round(user.totalDistance * 100) / 100}
              </div>
              <div>km</div>
            </div>
          </div>
        </div>
      </div>
      <div className="col">
        <div className="card activity-card">
          <div className="card-body row">
            <div className="col-3">
              <i className="fa fa-clock-o fa-3x fa-color" />
            </div>
            <div className="col-9 text-right">
              <div className="huge">{user.totalDuration}</div>
              <div>total duration</div>
            </div>
          </div>
        </div>
      </div>
      <div className="col">
        <div className="card activity-card">
          <div className="card-body row">
            <div className="col-3">
              <i className="fa fa-tags fa-3x fa-color" />
            </div>
            <div className="col-9 text-right">
              <div className="huge">{user.nbSports}</div>
              <div>{`sport${user.nbSports === 1 ? '' : 's'}`}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
