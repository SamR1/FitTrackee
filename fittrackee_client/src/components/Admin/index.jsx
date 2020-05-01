import React from 'react'
import { Helmet } from 'react-helmet'
import { withTranslation } from 'react-i18next'
import { connect } from 'react-redux'
import { Route, Switch } from 'react-router-dom'

import AdminApplication from './Application'
import AdminDashboard from './AdminDashboard'
import AdminSports from './Sports'
import AdminUsers from './Users'
import NotFound from './../Others/NotFound'

function Admin(props) {
  const { t, user } = props
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
              render={() => <AdminDashboard t={t} />}
            />
            <Route
              exact
              path="/admin/application"
              render={() => <AdminApplication t={t} />}
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
    user: state.user,
  }))(Admin)
)
