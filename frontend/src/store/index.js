import { createStore } from 'vuex'

export default createStore({
  state: {
    accessToken: null,
    tokenType: null
  },
  mutations: {
    SET_AUTH_DATA(state, { accessToken, tokenType }) {
      state.accessToken = accessToken
      state.tokenType = tokenType
    },
    CLEAR_AUTH_DATA(state) {
      state.accessToken = null
      state.tokenType = null
    }
  },
  actions: {},
  getters: {
    isAuthenticated: state => !!state.accessToken,
    getAuthHeader: state =>  {
        if (state.accessToken && state.tokenType) {
          return `${state.tokenType} ${state.accessToken}`
        }
        return '登録なし'
      }
    }
})