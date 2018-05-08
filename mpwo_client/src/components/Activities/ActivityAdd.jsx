import React from 'react'
import { Helmet } from 'react-helmet'
import { connect } from 'react-redux'

import FormWithGpx from './ActivityForms/FormWithGpx'
import { getData } from '../../actions/index'


class AddActivity extends React.Component {
  componentDidMount() {
      this.props.loadSports()
  }

  render() {
    const { message, sports } = this.props
    return (
      <div>
        <Helmet>
          <title>mpwo - Add an activity</title>
        </Helmet>
        <br /><br />
        {message && (
          <code>{message}</code>
        )}

        <div className="container">
          <div className="row">
            <div className="col-md-2" />
            <div className="col-md-8">
              <div className="card add-activity">
                <h2 className="card-header text-center">
                  Add a sport
                </h2>
                <div className="card-body">
                  <FormWithGpx sports={sports} />
                </div>
              </div>
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
    message: state.message,
    sports: state.sports.data,
    user: state.user,
  }),
  dispatch => ({
    loadSports: () => {
      dispatch(getData('sports'))
    },
  })
)(AddActivity)
