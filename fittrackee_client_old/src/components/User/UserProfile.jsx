import React from 'react'
import { withTranslation } from 'react-i18next'
import { connect } from 'react-redux'

import CustomModal from '../Common/CustomModal'
import ProfileDetail from './ProfileDetail'
import { getOrUpdateData } from '../../actions'
import { deleteUser } from '../../actions/user'

class UserProfile extends React.Component {
  constructor(props, context) {
    super(props, context)
    this.state = {
      displayModal: false,
    }
  }

  componentDidMount() {
    this.props.loadUser(this.props.match.params.userName)
  }

  componentDidUpdate(prevProps) {
    if (prevProps.match.params.userName !== this.props.match.params.userName) {
      this.props.loadUser(this.props.match.params.userName)
    }
  }

  displayModal(value) {
    this.setState(prevState => ({
      ...prevState,
      displayModal: value,
    }))
  }

  render() {
    const { t, currentUser, onDeleteUser, users } = this.props
    const { displayModal } = this.state
    const [user] = users
    const editable = user ? currentUser.username === user.username : false
    return (
      <div>
        {displayModal && (
          <CustomModal
            title={t('common:Confirmation')}
            text={t(
              'user:Are you sure you want to delete this account? ' +
                'All data will be deleted, this cannot be undone.'
            )}
            confirm={() => {
              onDeleteUser(user.username)
              this.displayModal(false)
            }}
            close={() => this.displayModal(false)}
          />
        )}
        {user && (
          <ProfileDetail
            editable={editable}
            isDeletable={currentUser.admin && !editable}
            onDeleteUser={onDeleteUser}
            displayModal={e => this.displayModal(e)}
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
      onDeleteUser: username => {
        dispatch(deleteUser(username, true))
      },
      loadUser: userName => {
        dispatch(getOrUpdateData('getData', 'users', { username: userName }))
      },
    })
  )(UserProfile)
)
