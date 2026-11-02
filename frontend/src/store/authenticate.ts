import { defineStore } from "pinia";
import { UserRole } from "@/views/types/auth";

export const useAuthStore = defineStore("authStore", {
  state: () => ({
    accessToken: "",
    tokenType: "",
    expire: 0,
    redirectPath: "",
    role: "",
    mustChangePassword: false,
  }),
  getters: {
    isToken(): boolean {
      return Boolean(this.accessToken);
    },
    getAuthHeader(): string | null {
      if (!this.accessToken && !this.tokenType) {
        return null;
      }
      return `${this.tokenType} ${this.accessToken}`;
    },
    getRedirectPath(): string {
      return this.redirectPath;
    },
  },
  actions: {
    setAuthData(
      accessToken: string,
      tokenType: string,
      expire: number,
      mustChangePassword: boolean,
    ) {
      if (!accessToken || !tokenType || !expire) {
        throw new Error("データに不備があります");
      }
      this.accessToken = accessToken;
      this.tokenType = tokenType;
      this.expire = expire;
      this.mustChangePassword = mustChangePassword;
    },
    clearAuthData() {
      this.accessToken = "";
      this.tokenType = "";
      this.expire = 0;
      this.mustChangePassword = false;
      this.redirectPath = "";
    },
    isExpired() {
      const currentTime = Date.now();
      if (currentTime / 1000 <= this.expire) {
        // 期限切れのトークンではない
        return false;
      } else {
        return true;
      }
    },
    setRedirectPath(path: string) {
      this.redirectPath = path;
    },
  },
});

type RoleState = {
  role: UserRole | "";
};

export const useRoleStore = defineStore("roleStore", {
  state: (): RoleState => ({
    role: "",
  }),
  getters: {
    getRole(): string {
      return this.role;
    },
  },
  actions: {
    setRole(role: UserRole) {
      this.role = role;
    },
    clearRole() {
      this.role = "";
    },
  },
  persist: true,
});
