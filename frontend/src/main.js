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
    // make sure a token exists
    (!authStore.isToken||
    // make sure the token is not expired
    authStore.isExpired())&&
    // ❗️ except Login and RegisterUser
    to.name !== 'Login' &&
    to.name !== 'RegisterUser'
  ) {
    // redirect the user to the login page
    return { name: 'Login' }
  }
})