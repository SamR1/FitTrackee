import React from 'react'
import { Helmet } from 'react-helmet'
import { connect } from 'react-redux'
import { Link } from 'react-router-dom'

class AdminMenu extends React.Component {
  componentDidMount() {}
  render() {
    return (
      <div>
        <Helmet>
          <title>mpwo - Admin</title>
        </Helmet>
        <h1 className="page-title">Administration</h1>
        <div className="container">
          <div className="row">
            <div className="col-md-2" />
            <div className="col-md-8 card">
              <ul>
                <li>
                  <Link
                    to={{
                      pathname: '/admin/sports',
                    }}
                  >
                    Sports
                  </Link>
                </li>
              </ul>
            </div>
            <div className="col-md-2" />
          </div>
        </div>
      </div>
    )
  }
}

export default connect(
  state => ({
    user: state.user,
  })
)(AdminMenu)
