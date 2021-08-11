import { Module } from 'vuex'
import { IRootState } from '@/store/modules/root/interfaces'
import { getters } from '@/store/modules/user/getters'
import { IUserState } from '@/store/modules/user/interfaces'
import { userState } from '@/store/modules/user/state.ts'

const user: Module<IUserState, IRootState> = {
  state: userState,
  getters,
}

export default user
