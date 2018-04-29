import React from 'react'
import { Helmet } from 'react-helmet'
import { connect } from 'react-redux'

import { getData } from '../../actions/index'

class AdminSports extends React.Component {
  componentDidMount() {
      this.props.loadSport()
  }
  render() {
    const { sports } = this.props
    return (
      <div>
        <Helmet>
          <title>mpwo - Admin</title>
        </Helmet>
        <h1 className="page-title">Administration - Sports</h1>
        <div className="container">
          <div className="row">
            <div className="col-md-2" />
            <div className="col-md-8 card">
              <ul className="sport-items">
                {sports.map(sport => (
                  <li key={sport.id}>
                      {sport.label}
                  </li>
                ))}
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
    sports: state.sports.data,
    user: state.user,
  }),
  dispatch => ({
    loadSport: () => {
      dispatch(getData('sports'))
    },
  })
)(AdminSports)
