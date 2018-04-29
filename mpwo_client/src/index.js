/* eslint-disable react/jsx-filename-extension */
import { createBrowserHistory } from 'history'
import React from 'react'
import ReactDOM from 'react-dom'
import { routerMiddleware } from 'react-router-redux'
import { applyMiddleware, createStore, compose } from 'redux'
import thunk from 'redux-thunk'

import App from './components/App'
import Root from './components/Root'
import registerServiceWorker from './registerServiceWorker'
import reducers from './reducers'
import { loadProfile } from './actions/user'

export const history = createBrowserHistory()

export const rootNode = document.getElementById('root')

export const store = createStore(
  reducers,
  window.__STATE__, // Server state
  (window.__REDUX_DEVTOOLS_EXTENSION_COMPOSE__ || compose)(
    applyMiddleware(routerMiddleware(history), thunk)
  )
)

if (window.localStorage.authToken !== null) {
  store.dispatch(loadProfile())
}

ReactDOM.render(
  <Root store={store} history={history}>
    <App />
  </Root>,
  rootNode
)
registerServiceWorker()
