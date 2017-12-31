import React from 'react'
import { Helmet } from 'react-helmet'
import { connect } from 'react-redux'

class Logout extends React.Component {
  componentDidMount() {}
  render() {
    return (
      <div>
        <Helmet>
          <title>mpwo - Dashboard</title>
        </Helmet>
        <h1 className="page-title">Dashboard</h1>
      </div>
    )
  }
}

export default connect(
  state => ({
    user: state.user,
  })
)(Logout)
