import { createStore } from 'vuex'

export default createStore({
  state: {
    language: 'en',
  },
  mutations: {
    setLanguage(state, language: string) {
      state.language = language
    },
  },
  actions: {},
  modules: {},
})
