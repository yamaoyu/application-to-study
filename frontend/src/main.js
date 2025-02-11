import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import { createPinia } from 'pinia';
import { useAuthStore } from '@/store/authenticate';
import axios from 'axios'
import { jwtDecode } from 'jwt-decode';
import { BootstrapVueNext } from 'bootstrap-vue-next'
import "bootstrap/dist/css/bootstrap.css";
import "bootstrap-vue-next/dist/bootstrap-vue-next.css";
import 'bootstrap/dist/js/bootstrap.bundle.min.js'

const pinia = createPinia();

createApp(App).use(router).use(pinia).use(BootstrapVueNext).mount('#app')

// トークンが無効、もしくはない場合はログインページとユーザー登録ページ以外は開けないようにする
const authStore = useAuthStore()
const ALLOWED_ROUTES = ['Login', 'RegisterUser']
const BACKEND_URL = process.env.VUE_APP_BACKEND_URL


const verfiyRefreshToken = async () => {
    // デバイス情報を取得 HTTPSにするまでの一時的な対応としてplatform(非推奨)を使用
  const device = navigator.platform || "unknown";
  const response = await axios.post(BACKEND_URL + "token",
    { device: device },
    { withCredentials: true })
  return response
}


router.beforeEach(async (to) => {
  // 遷移先がログインページとユーザー登録ページ以外の場合
  if (ALLOWED_ROUTES.includes(to.name)) {
    return
  }
  // トークンがない、もしくは期限切れの場合
  if (!authStore.isToken || authStore.isExpired()) {
    // リフレッシュトークンの検証
    try{
      const response = await verfiyRefreshToken()
      if (response.status === 200) {
        // トークンの更新
        await authStore.setAuthData(
          response.data.access_token,
          response.data.token_type,
          jwtDecode(response.data.access_token).exp)
      }
    } catch(error){
      return { name: 'Login' }
    }
  }
}
)