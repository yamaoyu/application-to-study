import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import { createPinia } from 'pinia';
import { useAuthStore } from '@/store/authenticate';
import { jwtDecode } from 'jwt-decode';
import { createBootstrap } from 'bootstrap-vue-next';
import "bootstrap/dist/css/bootstrap.css";
import "bootstrap-vue-next/dist/bootstrap-vue-next.css";
import 'bootstrap/dist/js/bootstrap.bundle.min.js'
import { verifyRefreshToken } from './views/lib';

const pinia = createPinia();

createApp(App).use(router).use(pinia).use(createBootstrap()).mount('#app')

// トークンが無効、もしくはない場合はログインページとユーザー登録ページ以外は開けないようにする
const authStore = useAuthStore()
const ALLOWED_ROUTES = ['Login', 'RegisterUser']


router.beforeEach(async (to) => {
  // ルートに飛ぶとユーザーホームへ遷移するようにする
  if (to.name===undefined){
    return { name: 'Home' }
  }
  console.log(to)
  // 遷移先がログインページとユーザー登録ページ以外の場合
  if (ALLOWED_ROUTES.includes(to.name)) {
    return
  }
  // トークンがない、もしくは期限切れの場合
  if (!authStore.isToken || authStore.isExpired()) {
    // リフレッシュトークンの検証
    try{
      const response = await verifyRefreshToken()
      if (response.status === 200) {
        // トークンの更新
        await authStore.setAuthData(
          response.data.access_token,
          response.data.token_type,
          jwtDecode(response.data.access_token).exp)
      }
    } catch(error){
      return { name: 'Login', message: '再度ログインしてください' }
    }
  }
}
)