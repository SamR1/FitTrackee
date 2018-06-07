import React from 'react'


export default function UserStatistics (props) {
  const { user } = props
  const days = user.totalDuration.match(/day/g)
    ? `${user.totalDuration.split(',')[0]},`
    : '0 days,'
  let duration = user.totalDuration.match(/day/g)
    ? user.totalDuration.split(', ')[1]
    : user.totalDuration
  duration = `${duration.split(':')[0]}h ${duration.split(':')[1]}min`
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
              <div>{`workout${user.nbActivities === 1 ? '' : 's'}`}</div>
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
                {Number(user.totalDistance).toFixed(2)}
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
              <div className="huge">{days}</div>
              <div>{duration}</div>
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
