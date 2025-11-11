import { defineStore } from 'pinia'

export const useAuthStore = defineStore('authStore', {
    state: () => ({
        accessToken: null,
        tokenType: null,
        expire: null,
        redirectPath: null,
        role: null
    }),
    getters: {
      isToken() {
        return Boolean(this.accessToken)
      },
      getAuthHeader() {
        if (!this.accessToken && !this.tokenType) {
            return '登録なし'
        }
        return `${this.tokenType} ${this.accessToken}`
      },
      getRedirectPath() {
        return this.redirectPath
      }
    },
    actions: {
      setAuthData(accessToken, tokenType, expire) {
        if (!accessToken || !tokenType || !expire) {
            throw new Error('データに不備があります')
        }
        this.accessToken = accessToken;
        this.tokenType = tokenType;
        this.expire = expire;
      },
      clearAuthData() {
        this.accessToken = null;
        this.tokenType = null;
        this.expire = null;
      },
      isExpired() {
        const currentTime = Date.now()
        if (currentTime/1000 <= this.expire){
        // 期限切れのトークンではない
            return false
        } else {
            return true
        }
      },
      setRedirectPath(path) {
        this.redirectPath = path;
      }
    },
  })

export const useRoleStore = defineStore('roleStore', {
  state: () => ({
    role: null
  }),
  getters: {
    getRole() {
      return this.role
    }
  },
  actions: {
    setRole(role) {
      this.role = role;
    },
    clearRole(){
      this.role = null;
    }
  },
  persist: true
})