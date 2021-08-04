import { UserStateTypes } from '@/types/state'

const userState = {
  authToken: null,
}

export type Getters = {
  isAuthenticated(state: UserStateTypes): boolean
}

const getters: Getters = {
  isAuthenticated(state: UserStateTypes) {
    return state.authToken !== null
  },
}
export default {
  state: userState,
  getters,
}
