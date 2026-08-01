import { createApp } from 'vue'
import App from './App.vue'
import router from './router/index'
import { createPinia } from 'pinia';
import { createPersistedState } from 'pinia-plugin-persistedstate';
import { useAuthStore } from '@/store/authenticate';
import { createBootstrap } from 'bootstrap-vue-next';
import "bootstrap/dist/css/bootstrap.css";
import "bootstrap-vue-next/dist/bootstrap-vue-next.css";
import 'bootstrap/dist/js/bootstrap.bundle.min.js'
import { verifyRefreshToken } from './views/api/auth.js';
import { setAuthDataFromToken } from './views/composables/useAuth.js';

const pinia = createPinia();
pinia.use(createPersistedState());
createApp(App).use(router).use(pinia).use(createBootstrap()).mount('#app')

// トークンが無効、もしくはない場合はログインページとユーザー登録ページ以外は開けないようにする
const authStore = useAuthStore(pinia)
const ALLOWED_ROUTES = ['Login', 'RegisterUser']


router.beforeEach(async (to) => {
  // ルートに飛ぶとユーザーホームへ遷移するようにする
  const destination = to.name;
  if (typeof destination !== "string") {
    return { name: 'Home' }
  }
  // 遷移先がログインページとユーザー登録ページ以外の場合
  if (ALLOWED_ROUTES.includes(destination)) {
    // トークンがあればホームページへ
    try {
      const response = await verifyRefreshToken()
      if (response.status === 200) {
        return { name: 'Home' }
      }
      // トークンがなければそのまま
      return
    } catch {
      return
    }
  }
  // トークンがない、もしくは期限切れの場合
  if (!authStore.isToken || authStore.isExpired()) {
    // リフレッシュトークンの検証
    try {
      const response = await verifyRefreshToken()
      await setAuthDataFromToken(authStore, response.data)
    } catch {
      authStore.setRedirectPath(to.path)
      return { name: 'Login', message: '再度ログインしてください' }
    }
  }
}
)
