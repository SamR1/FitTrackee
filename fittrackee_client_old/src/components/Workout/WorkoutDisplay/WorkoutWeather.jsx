import React from 'react'

export default function WorkoutWeather(props) {
  const { t, workout } = props
  return (
    <div className="container">
      {workout.weather_start && workout.weather_end && (
        <table className="table table-borderless weather-table text-center">
          <thead>
            <tr>
              <th />
              <th>
                {t('workouts:Start')}
                <br />
                <img
                  className="weather-img"
                  src={`/img/weather/${workout.weather_start.icon}.png`}
                  alt={`workout weather (${workout.weather_start.icon})`}
                  title={workout.weather_start.summary}
                />
              </th>
              <th>
                {t('workouts:End')}
                <br />
                <img
                  className="weather-img"
                  src={`/img/weather/${workout.weather_end.icon}.png`}
                  alt={`workout weather (${workout.weather_end.icon})`}
                  title={workout.weather_end.summary}
                />
              </th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>
                <img
                  className="weather-img-small"
                  src="/img/weather/temperature.png"
                  alt="Temperatures"
                />
              </td>
              <td>{Number(workout.weather_start.temperature).toFixed(1)}°C</td>
              <td>{Number(workout.weather_end.temperature).toFixed(1)}°C</td>
            </tr>
            <tr>
              <td>
                <img
                  className="weather-img-small"
                  src="/img/weather/pour-rain.png"
                  alt="Temperatures"
                />
              </td>
              <td>
                {Number(workout.weather_start.humidity * 100).toFixed(1)}%
              </td>
              <td>{Number(workout.weather_end.humidity * 100).toFixed(1)}%</td>
            </tr>
            <tr>
              <td>
                <img
                  className="weather-img-small"
                  src="/img/weather/breeze.png"
                  alt="Temperatures"
                />
              </td>
              <td>{Number(workout.weather_start.wind).toFixed(1)}m/s</td>
              <td>{Number(workout.weather_end.wind).toFixed(1)}m/s</td>
            </tr>
          </tbody>
        </table>
      )}
    </div>
  )
}
