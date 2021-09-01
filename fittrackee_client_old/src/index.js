/* eslint-disable react/jsx-filename-extension */
import { createBrowserHistory } from 'history'
import React from 'react'
import { I18nextProvider } from 'react-i18next'
import ReactDOM from 'react-dom'
import { routerMiddleware } from 'connected-react-router'
import { applyMiddleware, compose, createStore } from 'redux'
import thunk from 'redux-thunk'

import i18n from './i18n'
import App from './components/App'
import Root from './components/Root'
import registerServiceWorker from './registerServiceWorker'
import createRootReducer from './reducers'
import { loadProfile } from './actions/user'
import { historyEnhancer } from './utils/history'

export const history = historyEnhancer(createBrowserHistory())

history.listen(() => {
  window.scrollTo(0, 0)
})

export const rootNode = document.getElementById('root')

export const store = createStore(
  createRootReducer(history),
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
    <I18nextProvider i18n={i18n}>
      <App />
    </I18nextProvider>
  </Root>,
  rootNode
)
registerServiceWorker()
