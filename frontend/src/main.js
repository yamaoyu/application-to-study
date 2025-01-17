import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import { createPinia } from 'pinia';
import { useAuthStore } from '@/store/authenticate';
import axios from 'axios'
import { jwtDecode } from 'jwt-decode';

const pinia = createPinia();

createApp(App).use(router).use(pinia).mount('#app')

// トークンが無効、もしくはない場合はログインページとユーザー登録ページ以外は開けないようにする
const authStore = useAuthStore()
router.beforeEach(async (to) => {
  // 遷移先がログインページとユーザー登録ページ以外の場合
  if (to.name !== 'Login' && to.name !== 'RegisterUser') {
    // トークンがない、もしくは期限切れの場合
    if (!authStore.isToken || authStore.isExpired()) {
      // リフレッシュトークンの検証
      try{
        const device = navigator.userAgentData?.platform || "unknown";
        const response = await axios.post(
          process.env.VUE_APP_BACKEND_URL + "token", 
          { device: device },
          { withCredentials: true })
        if (response.status === 200) {
          // トークンの更新
          await authStore.setAuthData(
            response.data.access_token,
            response.data.token_type,
            jwtDecode(response.data.access_token).exp)
        } else {
          return { name: 'Login' }
        }
      } catch(error){
        return { name: 'Login' }
      }
    }
  }
})