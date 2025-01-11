import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import { createPinia } from 'pinia';
import { useAuthStore } from '@/store/authenticate';

const pinia = createPinia();

createApp(App).use(router).use(pinia).mount('#app')

// トークンが無効、もしくはない場合はログインページとユーザー登録ページ以外は開けないようにする
const authStore = useAuthStore()
router.beforeEach(async (to) => {
  if (
    // トークンがあることを確認
    (!authStore.isToken||
    // トークンの期限を確認
    authStore.isExpired())&&
    // 遷移先がログインページとユーザー登録ページは除く
    to.name !== 'Login' &&
    to.name !== 'RegisterUser'
  ) {
    return { name: 'Login' }
  }
})