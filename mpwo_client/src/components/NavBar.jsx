import React from 'react'

export default class NavBar extends React.Component {
  constructor(props) {
    super(props)
    this.props = props
  }

  render() {
    return (
    <header>
      <nav className="navbar navbar-expand-lg navbar-light bg-light">
        <span className="navbar-brand">mpwo</span>
        <button
            className="navbar-toggler"
            type="button"
            data-toggle="collapse"
            data-target="#navbarSupportedContent"
            aria-controls="navbarSupportedContent"
            aria-expanded="false"
            aria-label="Toggle navigation"
        >
          <span className="navbar-toggler-icon" />
        </button>

        <div className="collapse navbar-collapse" id="navbarSupportedContent">
          <ul className="navbar-nav mr-auto">
            <li className="nav-item">
              <a className="nav-link" href="/">Home</a>
            </li>
          </ul>
        </div>
      </nav>
    </header>
    )
  }
}
