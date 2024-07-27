import { createRouter, createWebHistory } from 'vue-router'
import RegisterView from '../components/RegisterForm.vue'
import HelloWorld from '../components/HelloWorld.vue'
import LoginView from '../components/LoginForm.vue'

const routes = [
  {
    path: '/register',
    name: 'Register',
    component: RegisterView
  },
  {
    path: '/',
    name: 'HelloWord',
    component: HelloWorld
  },
  {
    path:'/login',
    name:'Login',
    component: LoginView
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router