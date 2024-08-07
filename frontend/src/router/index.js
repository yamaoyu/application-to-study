import { createRouter, createWebHistory } from 'vue-router'
import RegisterUser from '../components/RegisterUser.vue'
import HelloWorld from '../components/HelloWorld.vue'
import LoginView from '../components/LoginForm.vue'
import UserHomeView from '../components/UserHome.vue'
import RegisterIncome from '../components/RegisterIncome.vue'
import RegisterTarget from '../components/RegisterTarget.vue'
import RegisterActual from '../components/RegisterActual.vue'
import MonthlyInfo from '../components/MonthlyInfo.vue'


const routes = [
  {
    path: '/form/user',
    name: 'RegisterUser',
    component: RegisterUser
  
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
  },
  {
    path:'/home',
    name:'Home',
    component: UserHomeView
  },
  {
    path:'/form/income',
    name:'RegisterIncome',
    component: RegisterIncome
  },
  {
    path:"/form/target",
    name:"RegisterTarget",
    component:RegisterTarget
  },
  {
    path:"/form/actual",
    name:"RegisterActual",
    component:RegisterActual
  },
  {
    path:"/month",
    name:"MonthlyInfo",
    component:MonthlyInfo
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router