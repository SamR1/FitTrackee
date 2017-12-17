const user = (state = null, action) => {
  switch (action.type) {
    case 'AUTH_ERROR':
    case 'PROFILE_ERROR':
    case 'LOGOUT':
      window.localStorage.removeItem('authToken')
      return null
    case 'PROFILE_SUCCESS':
      return {
        id: action.message.data.id,
        username: action.message.data.username,
        email: action.message.data.email,
        isAdmin: action.message.data.is_admin,
        createdAt: action.message.data.created_at,
      }
    default:
      return state
  }
}

export default user
