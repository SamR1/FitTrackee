import React from 'react'
import { Helmet } from 'react-helmet'
import { Link } from 'react-router-dom'

import { history } from '../../../index'

export default function AdminPage(props) {

  const { data, detailLink, target } = props
  const { error } = data
  const results = data.data
  const tbKeys = []
  if (results.length > 0) {
    Object.keys(results[0])
      .filter(key => key.charAt(0) !== '_')
      .map(key => tbKeys.push(key))
  }
  const title = target.charAt(0).toUpperCase() + target.slice(1)

  return (
    <div>
      <Helmet>
        <title>mpwo - Admin</title>
      </Helmet>
      <h1 className="page-title">
          Administration - {title}
      </h1>
      {error ? (
        <code>{error}</code>
      ) : (
        <div className="container">
          <div className="row">
            <div className="col-md-2" />
            <div className="col-md-8 card">
              <div className="card-body">
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
                      // eslint-disable-next-line react/no-array-index-key
                      <tr key={idx}>
                        { Object.keys(result)
                          .filter(key => key.charAt(0) !== '_')
                          .map(key => {
                          if (key === 'id') {
                            return (
                              <th key={key} scope="row">
                              <Link to={`/admin/${detailLink}/${result[key]}`}>
                                {result[key]}
                              </Link>
                              </th>
                            )
                          }
                          return <td key={key}>{result[key]}</td>
                          })
                        }
                      </tr>
                    ))}
                  </tbody>
                </table>
                <input
                  type="submit"
                  className="btn btn-primary btn-lg btn-block"
                  onClick={() => history.push(`/admin/${target}/add`)}
                  value="Add a new item"
                />
                <input
                  type="submit"
                  className="btn btn-secondary btn-lg btn-block"
                  onClick={() => history.push('/admin/')}
                  value="Back"
                />
              </div>
            </div>
          <div className="col-md-2" />
        </div>
      </div>
      )}

    </div>
  )
}
