import React from 'react'


export default function UserStatistics (props) {
  const { user } = props
  const days = user.total_duration.match(/day/g)
    ? `${user.total_duration.split(',')[0]},`
    : '0 days,'
  let duration = user.total_duration.match(/day/g)
    ? user.total_duration.split(', ')[1]
    : user.total_duration
  duration = `${duration.split(':')[0]}h ${duration.split(':')[1]}min`
  return (
    <div className="row">
      <div className="col-md-3">
        <div className="card activity-card">
          <div className="card-body row">
            <div className="col-3">
              <i className="fa fa-calendar fa-3x fa-color" />
            </div>
            <div className="col-9 text-right">
              <div className="huge">{user.nb_activities}</div>
              <div>{`workout${user.nb_activities === 1 ? '' : 's'}`}</div>
            </div>
          </div>
        </div>
      </div>
      <div className="col-md-3">
        <div className="card activity-card">
          <div className="card-body row">
            <div className="col-3">
              <i className="fa fa-road fa-3x fa-color" />
            </div>
            <div className="col-9 text-right">
              <div className="huge">
                {Number(user.total_distance).toFixed(2)}
              </div>
              <div>km</div>
            </div>
          </div>
        </div>
      </div>
      <div className="col-md-3">
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
      <div className="col-md-3">
        <div className="card activity-card">
          <div className="card-body row">
            <div className="col-3">
              <i className="fa fa-tags fa-3x fa-color" />
            </div>
            <div className="col-9 text-right">
              <div className="huge">{user.nb_sports}</div>
              <div>{`sport${user.nb_sports === 1 ? '' : 's'}`}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
