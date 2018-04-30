import React from 'react'
import { Helmet } from 'react-helmet'


export default function AdminPage(props) {

  const { target, data } = props
  const error = data.error
  const results = data.data
  const tbKeys = []
  if (results.length > 0) {
    Object.keys(results[0]).map(key => tbKeys.push(key))
  }
  const title = target.charAt(0).toUpperCase() + target.slice(1)

  return (
    <div>
      <Helmet>
        <title>mpwo - Admin</title>
      </Helmet>
      {error && (
        <code>{error}</code>
      )}
      <h1 className="page-title">
          Administration - {title}
      </h1>
      <div className="container">
        <div className="row">
          <div className="col-md-2" />
          <div className="col-md-8 card">

            <table className="table">
              <thead>
                <tr>
                  {tbKeys.map(
                      tbKey => <th key={tbKey} scope="col">{tbKey}</th>
                  )}
                </tr>
              </thead>
              <tbody>
                { results.map((result, idx) => (
                  <tr key={idx}>
                    { Object.keys(result).map(key => {
                      if (key === 'id') {
                        return <th key={key} scope="row">{result[key]}</th>
                      }
                      return <td key={key}>{result[key]}</td>
                  }) }
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div className="col-md-2" />
        </div>
      </div>
    </div>
  )
}
