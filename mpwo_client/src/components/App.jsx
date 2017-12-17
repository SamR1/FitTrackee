import React from 'react'

import './App.css'
import NavBar from './NavBar'

export default class App extends React.Component {
  constructor(props) {
    super(props)
    this.props = props
  }

  render() {
    return (
      <div className="App">
        <NavBar />
        <p className="App-body">
          App in progress
        </p>
      </div>
    )
  }
}
