import { defineStore } from 'pinia'
import { UserRole } from '@/views/types/auth'

export const useAuthStore = defineStore('authStore', {
  state: () => ({
    accessToken: "",
    tokenType: "",
    expire: 0,
    redirectPath: "",
    role: ""
  }),
  getters: {
    isToken(): boolean {
      return Boolean(this.accessToken)
    },
    getAuthHeader(): string {
      if (!this.accessToken && !this.tokenType) {
        return '登録なし'
      }
      return `${this.tokenType} ${this.accessToken}`
    },
    getRedirectPath(): string {
      return this.redirectPath
    }
  },
  actions: {
    setAuthData(accessToken: string, tokenType: string, expire: number) {
      if (!accessToken || !tokenType || !expire) {
        throw new Error('データに不備があります')
      }
      this.accessToken = accessToken;
      this.tokenType = tokenType;
      this.expire = expire;
    },
    clearAuthData() {
      this.accessToken = "";
      this.tokenType = "";
      this.expire = 0;
    },
    isExpired() {
      const currentTime = Date.now()
      if (currentTime / 1000 <= this.expire) {
        // 期限切れのトークンではない
        return false
      } else {
        return true
      }
    },
    setRedirectPath(path: string) {
      this.redirectPath = path;
    }
  },
})

type RoleState = {
  role: UserRole | "";
};


export const useRoleStore = defineStore('roleStore', {
  state: (): RoleState => ({
    role: ""
  }),
  getters: {
    getRole(): string {
      return this.role
    }
  },
  actions: {
    setRole(role: UserRole) {
      this.role = role;
    },
    clearRole() {
      this.role = "";
    }
  },
  persist: true
})