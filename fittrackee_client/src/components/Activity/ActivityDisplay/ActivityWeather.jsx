import React from 'react'

export default function ActivityWeather(props) {
  const { activity } = props
  return (
    <div className="container">
      {activity.weather_start && activity.weather_end && (
        <table className="table table-borderless weather-table text-center">
          <thead>
            <tr>
              <th />
              <th>
                Start
                <br />
                <img
                  className="weather-img"
                  src={`/img/weather/${activity.weather_start.icon}.png`}
                  alt={`activity weather (${activity.weather_start.icon})`}
                  title={activity.weather_start.summary}
                />
              </th>
              <th>
                End
                <br />
                <img
                  className="weather-img"
                  src={`/img/weather/${activity.weather_end.icon}.png`}
                  alt={`activity weather (${activity.weather_end.icon})`}
                  title={activity.weather_end.summary}
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
              <td>{Number(activity.weather_start.temperature).toFixed(1)}°C</td>
              <td>{Number(activity.weather_end.temperature).toFixed(1)}°C</td>
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
                {Number(activity.weather_start.humidity * 100).toFixed(1)}%
              </td>
              <td>{Number(activity.weather_end.humidity * 100).toFixed(1)}%</td>
            </tr>
            <tr>
              <td>
                <img
                  className="weather-img-small"
                  src="/img/weather/breeze.png"
                  alt="Temperatures"
                />
              </td>
              <td>{Number(activity.weather_start.wind).toFixed(1)}m/s</td>
              <td>{Number(activity.weather_end.wind).toFixed(1)}m/s</td>
            </tr>
          </tbody>
        </table>
      )}
    </div>
  )
}
