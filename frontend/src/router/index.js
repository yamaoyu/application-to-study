import { createRouter, createWebHistory } from 'vue-router'
import RegisterUser from '../views/RegisterUser.vue'
import LoginView from '../views/LoginForm.vue'
import UserHomeView from '../views/UserHome.vue'
import RegisterSalary from '../views/RegisterSalary.vue'
import RegisterTarget from '../views/RegisterTarget.vue'
import RegisterActual from '../views/RegisterActual.vue'
import MonthlyInfo from '../views/MonthlyInfo.vue'
import RegisterTodo from '../views/RegisterTodo.vue'
import finishActivity from '../views/FinishActivity.vue'
import InquiryForm from '../views/InquiryForm.vue'
import AllPeriodInfo from '../views/AllPeriodInfo.vue'
import EditTodo from '../views/EditTodo.vue'
import store from '../store/index.js'

const routes = [
  {
    path: '/register/user',
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
    path:'/register/salary',
    name:'RegisterSalary',
    component: RegisterSalary
  },
  {
    path:"/register/target",
    name:"RegisterTarget",
    component:RegisterTarget
  },
  {
    path:"/register/actual",
    name:"RegisterActual",
    component:RegisterActual
  },
  {
    path:"/view/month-activities",
    name:"MonthlyInfo",
    component:MonthlyInfo
  },
  {
    path:"/register/todo",
    name:"RegisterTodo",
    component:RegisterTodo
  },
  {
    path:"/finish/activity",
    name:"finishActivity",
    component:finishActivity
  },
  {
    path:"/register/inquiry",
    name:"InquiryForm",
    component:InquiryForm
  },
  {
    path:"/view/all-activities",
    name:"AllPeriodInfo",
    component:AllPeriodInfo
  },
  {
    path:"/edit/todo",
    name:"EditTodo",
    component:EditTodo
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})


router.beforeEach(async (to) => {
  if (
    // make sure a token exists
    (!store.getters["authenticateModule/isToken"] ||
    // make sure the token is not expired
    store.getters["authenticateModule/isExpired"])&&
    // ❗️ except Login and RegisterUser
    to.name !== 'Login' &&
    to.name !== 'RegisterUser'
  ) {
    // redirect the user to the login page
    return { name: 'Login' }
  }
})

export default router