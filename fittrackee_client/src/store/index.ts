import { createStore } from 'vuex'
import { DefaultStateTypes } from '@/types/state'
import user from './modules/user'

export default createStore({
  state: {
    language: 'en',
  },
  mutations: {
    setLanguage(state: DefaultStateTypes, language: string) {
      state.language = language
    },
  },
  actions: {},
  modules: {
    user,
  },
})
