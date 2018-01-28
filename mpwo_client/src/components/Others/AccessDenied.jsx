import React from 'react'
import { Helmet } from 'react-helmet'
import { connect } from 'react-redux'

class AccessDenied extends React.Component {
  componentDidMount() {}
  render() {
    return (
      <div>
        <Helmet>
          <title>mpwo - Access denied</title>
        </Helmet>
        <h1 className="page-title">Access denied</h1>
        <p className="App-center">
          {'You don\'t have permissions to access this page.'}
        </p>
      </div>
    )
  }
}

export default connect(
  state => ({
    user: state.user,
  })
)(AccessDenied)
