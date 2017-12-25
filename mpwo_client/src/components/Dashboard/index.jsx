import React from 'react'
import { connect } from 'react-redux'

class Logout extends React.Component {
  componentDidMount() {}
  render() {
    return (
      <div>
        <h1>Dashboard</h1>
      </div>
    )
  }
}

export default connect(
  state => ({
    user: state.user,
  })
)(Logout)
