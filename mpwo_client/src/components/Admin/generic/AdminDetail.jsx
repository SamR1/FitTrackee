import React from 'react'
import { Helmet } from 'react-helmet'
import { connect } from 'react-redux'
import { Link } from 'react-router-dom'

import { updateData } from '../../../actions/index'

class AdminDetail extends React.Component {

  constructor(props, context) {
    super(props, context)
    this.state = {
      isInEdition: false,
    }
  }

  render() {
    const {
      message,
      onDataUpdate,
      results,
      target,
    } = this.props
    const { isInEdition } = this.state
    const title = target.charAt(0).toUpperCase() + target.slice(1)

    return (
      <div>
        <Helmet>
          <title>mpwo - Admin</title>
        </Helmet>
        <h1 className="page-title">
            Administration - {title}
        </h1>
        {message ? (
          <code>{message}</code>
        ) : (
          results.length === 1 && (
          <div className="container">
            <div className="row">
              <div className="col-md-2" />
              <div className="col-md-8 card">
                <div className="card-body">
                  <form onSubmit={event =>
                   event.preventDefault()}
                  >
                    { results.map(result => (
                      Object.keys(result).map(key => (
                        <div className="form-group" key={key}>
                          <label>
                            {key}:
                            <input
                              className="form-control input-lg"
                              name={key}
                              readOnly={key === 'id' || !isInEdition}
                              defaultValue={result[key]}
                            />
                          </label>
                        </div>
                      ))
                    ))}
                    {isInEdition ? (
                      <div>
                        <input
                          type="submit"
                          className="btn btn-primary btn-lg btn-block"
                          onClick={event => {
                              onDataUpdate(event, target)
                              this.setState({ isInEdition: false })
                            }
                          }
                          value="Submit"
                        />
                        <input
                          type="submit"
                          className="btn btn-secondary btn-lg btn-block"
                          onClick={event => {
                            event.target.form.reset()
                            this.setState({ isInEdition: false })
                          }}
                          value="Cancel"
                        />
                      </div>
                    ) : (
                      <div>
                        <input
                          type="submit"
                          className="btn btn-primary btn-lg btn-block"
                          onClick={() => this.setState({ isInEdition: true })}
                          value="Edit"
                        />
                        <input
                          type="submit"
                          className="btn btn-danger btn-lg btn-block"
                          value="Delete"
                        />
                      </div>
                    )}
                  </form>
                  <Link to={`/admin/${target}`}>Back to the list</Link>
                </div>
              </div>
              <div className="col-md-2" />
            </div>
          </div>
          )
        )}
      </div>
    )
  }
}

export default connect(
  state => ({
    message: state.message,
  }),
  dispatch => ({
    onDataUpdate: (e, target) => {
      const data = [].slice
        .call(e.target.form.elements)
        .reduce(function(map, obj) {
          if (obj.name) {
            map[obj.name] = obj.value
          }
          return map
        }, {})
      dispatch(updateData(target, data))
    },
  })
)(AdminDetail)
