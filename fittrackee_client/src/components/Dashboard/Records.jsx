import React from 'react'
import { Link } from 'react-router-dom'

import { formatRecord, translateSports } from '../../utils/activities'

export default function RecordsCard(props) {
  const { records, sports, t, user } = props
  const translatedSports = translateSports(sports, t)
  const recordsBySport = records.reduce((sportList, record) => {
    const sport = translatedSports.find(s => s.id === record.sport_id)
    if (sportList[sport.label] === void 0) {
      sportList[sport.label] = {
        img: sport.img,
        records: [],
      }
    }
    sportList[sport.label].records.push(formatRecord(record, user.timezone))
    return sportList
  }, {})

  return (
    <div className="card activity-card">
      <div className="card-header">{t('activities:Personal records')}</div>
      <div className="card-body">
        {Object.keys(recordsBySport).length === 0
          ? t('common:No records.')
          : Object.keys(recordsBySport)
              .sort()
              .map(sportLabel => (
                <table
                  className="table table-borderless table-sm record-table"
                  key={sportLabel}
                >
                  <thead>
                    <tr>
                      <th colSpan="3">
                        <img
                          alt={`${sportLabel} logo`}
                          className="record-logo"
                          src={recordsBySport[sportLabel].img}
                        />
                        {sportLabel}
                      </th>
                    </tr>
                  </thead>
                  <tbody>
                    {recordsBySport[sportLabel].records.map(rec => (
                      <tr key={rec.id}>
                        <td>{t(`activities:${rec.record_type}`)}</td>
                        <td className="text-right">{rec.value}</td>
                        <td className="text-right">
                          <Link to={`/activities/${rec.activity_id}`}>
                            {rec.activity_date}
                          </Link>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              ))}
      </div>
    </div>
  )
}
