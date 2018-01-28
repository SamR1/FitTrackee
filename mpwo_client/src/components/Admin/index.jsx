import React from 'react'
import { Helmet } from 'react-helmet'
import { connect } from 'react-redux'

import AccessDenied from './../Others/AccessDenied'

class Admin extends React.Component {
  componentDidMount() {}
  render() {
    const { user } = this.props
    return (
      <div>
        <Helmet>
          <title>mpwo - Admin</title>
        </Helmet>
        {!user.isAdmin ? (
            <AccessDenied />
        ) : (
          <h1 className="page-title">Admin</h1>
        )}
      </div>
    )
  }
}

export default connect(
  state => ({
    user: state.user,
  })
)(Admin)
