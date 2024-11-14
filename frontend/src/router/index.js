import { createRouter, createWebHistory } from 'vue-router'
import RegisterUser from '../views/RegisterUser.vue'
import LoginView from '../views/LoginForm.vue'
import UserHomeView from '../views/UserHome.vue'
import RegisterIncome from '../views/RegisterIncome.vue'
import RegisterTarget from '../views/RegisterTarget.vue'
import RegisterActual from '../views/RegisterActual.vue'
import MonthlyInfo from '../views/MonthlyInfo.vue'
import RegisterTodo from '../views/RegisterTodo.vue'
import finishActivity from '../views/FinishActivity.vue'
import InquiryForm from '../views/InquiryForm.vue'
import AllPeriodInfo from '../views/AllPeriodInfo.vue'

const routes = [
  {
    path: '/form/user',
    name: 'RegisterUser',
    component: RegisterUser
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
  },
  {
    path:"/form/todo",
    name:"RegisterTodo",
    component:RegisterTodo
  },
  {
    path:"/finish/activity",
    name:"finishActivity",
    component:finishActivity
  },
  {
    path:"/form/inquiry",
    name:"InquiryForm",
    component:InquiryForm
  },
  {
    path:"/all",
    name:"AllPeriodInfo",
    component:AllPeriodInfo
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router