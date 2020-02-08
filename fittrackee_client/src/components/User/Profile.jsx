import React from 'react'
import { withTranslation } from 'react-i18next'
import { connect } from 'react-redux'

import ProfileDetail from './ProfileDetail'

function Profile({ t, user }) {
  return (
    <div>
      <ProfileDetail t={t} user={user} />
    </div>
  )
}

export default withTranslation()(
  connect(state => ({
    user: state.user,
  }))(Profile)
)
