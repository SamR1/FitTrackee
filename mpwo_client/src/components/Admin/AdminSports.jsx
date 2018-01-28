import React from 'react'
import { Helmet } from 'react-helmet'
import { connect } from 'react-redux'

class AdminSports extends React.Component {
  componentDidMount() {}
  render() {
    return (
      <div>
        <Helmet>
          <title>mpwo - Admin</title>
        </Helmet>
        <h1 className="page-title">Administration - Sports</h1>
      </div>
    )
  }
}

export default connect(
  state => ({
    user: state.user,
  })
)(AdminSports)
