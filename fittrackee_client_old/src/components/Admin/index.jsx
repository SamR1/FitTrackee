import React from 'react'
import { Helmet } from 'react-helmet'
import { withTranslation } from 'react-i18next'
import { connect } from 'react-redux'
import { Route, Switch } from 'react-router-dom'

import AdminApplication from './AdminApplication'
import AdminDashboard from './AdminDashboard'
import AdminSports from './AdminSports'
import AdminUsers from './AdminUsers'
import NotFound from './../Others/NotFound'

function Admin(props) {
  const { appConfig, t, user } = props
  return (
    <>
      <Helmet>
        <title>FitTrackee - {t('administration:Administration')}</title>
      </Helmet>
      <div className="container dashboard">
        {user.admin ? (
          <Switch>
            <Route
              exact
              path="/admin"
              render={() => <AdminDashboard appConfig={appConfig} t={t} />}
            />
            <Route
              exact
              path="/admin/application"
              render={() => (
                <AdminApplication
                  appConfig={appConfig}
                  t={t}
                  isInEdition={false}
                />
              )}
            />
            <Route
              exact
              path="/admin/application/edit"
              render={() => (
                <AdminApplication appConfig={appConfig} t={t} isInEdition />
              )}
            />
            <Route
              exact
              path="/admin/sports"
              render={() => <AdminSports t={t} />}
            />
            <Route
              exact
              path="/admin/users"
              render={() => <AdminUsers t={t} />}
            />
            <Route component={NotFound} />
          </Switch>
        ) : (
          <NotFound />
        )}
      </div>
    </>
  )
}

export default withTranslation()(
  connect(state => ({
    appConfig: state.application.config,
    user: state.user,
  }))(Admin)
)
