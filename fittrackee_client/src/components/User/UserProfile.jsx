import React from 'react'
import { withTranslation } from 'react-i18next'
import { connect } from 'react-redux'

import ProfileDetail from './ProfileDetail'
import { getOrUpdateData } from '../../actions'

class UserProfile extends React.Component {
  componentDidMount() {
    this.props.loadUser(this.props.match.params.userName)
  }

  componentDidUpdate(prevProps) {
    if (prevProps.match.params.userName !== this.props.match.params.userName) {
      this.props.loadUser(this.props.match.params.userName)
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
      loadUser: userName => {
        dispatch(getOrUpdateData('getData', 'users', { username: userName }))
      },
    })
  )(UserProfile)
)
