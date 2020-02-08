import React from 'react'
import { withTranslation } from 'react-i18next'
import { connect } from 'react-redux'

import ProfileDetail from './ProfileDetail'
import { getOrUpdateData } from '../../actions'

class UserProfile extends React.Component {
  componentDidMount() {
    this.props.loadUser(this.props.match.params.userId)
  }

  componentDidUpdate(prevProps) {
    if (prevProps.match.params.userId !== this.props.match.params.userId) {
      this.props.loadUser(this.props.match.params.userId)
    }
  }

  render() {
    const { t, currentUser, users } = this.props
    const [user] = users
    return (
      <div>
        {user && (
          <ProfileDetail
            editable={currentUser.id === user.id}
            t={t}
            user={user}
          />
        )}
      </div>
    )
  }
}

export default withTranslation()(
  connect(
    state => ({
      currentUser: state.user,
      users: state.users.data,
    }),
    dispatch => ({
      loadUser: userId => {
        dispatch(getOrUpdateData('getData', 'users', { id: userId }))
      },
    })
  )(UserProfile)
)
