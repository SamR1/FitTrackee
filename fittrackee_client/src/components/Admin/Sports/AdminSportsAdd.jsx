import React from 'react'
import { Helmet } from 'react-helmet'
import { connect } from 'react-redux'

import { addData } from '../../../actions/index'
import { history } from '../../../index'

class AdminSportsAdd extends React.Component {
  componentDidMount() {}

  render() {
    const { message, onAddSport } = this.props

    return (
      <div>
        <Helmet>
          <title>FitTrackee - Admin - Add Sport</title>
        </Helmet>
        <h1 className="page-title">Administration - Sport</h1>
        {message && <code>{message}</code>}

        <div className="container">
          <div className="row">
            <div className="col-md-2" />
            <div className="col-md-8">
              <div className="card">
                <div className="card-header">Add a sport</div>
                <div className="card-body">
                  <form onSubmit={event => event.preventDefault()}>
                    <div className="form-group">
                      <label>
                        Label:
                        <input
                          name="label"
                          className="form-control input-lg"
                          type="text"
                        />
                      </label>
                    </div>
                    <input
                      type="submit"
                      className="btn btn-primary btn-lg btn-block"
                      onClick={event => onAddSport(event)}
                      value="Submit"
                    />
                    <input
                      type="submit"
                      className="btn btn-secondary btn-lg btn-block"
                      onClick={() => history.push('/admin/sports')}
                      value="Cancel"
                    />
                  </form>
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
    user: state.user,
  }),
  dispatch => ({
    onAddSport: e => {
      const data = { label: e.target.form.label.value }
      dispatch(addData('sports', data))
    },
  })
)(AdminSportsAdd)
