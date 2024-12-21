export const authenticateModule = {
    namespaced: true,
    state: {
        accessToken: null,
        tokenType: null,
        expire: null,
    },
    mutations: {
    SET_AUTH_DATA(state, { accessToken, tokenType, expire }) {
        state.accessToken = accessToken
        state.tokenType = tokenType
        state.expire = expire
        },
    CLEAR_AUTH_DATA(state) {
        state.accessToken = null
        state.tokenType = null
        state.expire = null
        },
    },
    actions: {},
    getters: {
    isToken: state => !!state.accessToken,
    isExpired: state => {
        const currentTime = Date.now()
        if (currentTime/1000 <= state.expire){
        // 期限切れのトークンではない
        return false
        } else {
        return true
        }
        },
    getAuthHeader: state =>  {
        if (state.accessToken && state.tokenType) {
        return `${state.tokenType} ${state.accessToken}`
        } else {
        return '登録なし'
        }
        }
    }
}