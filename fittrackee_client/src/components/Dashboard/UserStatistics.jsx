import React from 'react'

export default function UserStatistics(props) {
  const { t, user } = props
  const days = user.total_duration.match(/day/g)
    ? `${user.total_duration.split(' ')[0]} ${
        user.total_duration.match(/days/g) ? t('common:days') : t('common:day')
      }`
    : `0 ${t('common:days')},`
  let duration = user.total_duration.match(/day/g)
    ? user.total_duration.split(', ')[1]
    : user.total_duration
  duration = `${duration.split(':')[0]}h ${duration.split(':')[1]}min`
  return (
    <div className="row">
      <div className="col-lg-3 col-md-6 col-sm-6">
        <div className="card workout-card">
          <div className="card-body row">
            <div className="col-3">
              <i className="fa fa-calendar fa-3x fa-color" />
            </div>
            <div className="col-9 text-right">
              <div className="huge">{user.nb_workouts}</div>
              <div>{`${
                user.nb_workouts === 1
                  ? t('common:workout')
                  : t('common:workouts')
              }`}</div>
            </div>
          </div>
        </div>
      </div>
      <div className="col-lg-3 col-md-6 col-sm-6">
        <div className="card workout-card">
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
      <div className="col-lg-3 col-md-6 col-sm-6">
        <div className="card workout-card">
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
      <div className="col-lg-3 col-md-6 col-sm-6">
        <div className="card workout-card">
          <div className="card-body row">
            <div className="col-3">
              <i className="fa fa-tags fa-3x fa-color" />
            </div>
            <div className="col-9 text-right">
              <div className="huge">{user.nb_sports}</div>
              <div>{`${
                user.nb_sports === 1 ? t('common:sport') : t('common:sports')
              }`}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
