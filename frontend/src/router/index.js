import { createRouter, createWebHistory } from 'vue-router'
import RegisterUser from '../views/RegisterUser.vue'
import LoginView from '../views/LoginForm.vue'
import UserHomeView from '../views/UserHome.vue'
import RegisterSalary from '../views/RegisterSalary.vue'
import RegisterTodo from '../views/RegisterTodo.vue'
import InquiryForm from '../views/InquiryForm.vue'
import UserInfo from '../views/UserInfo.vue'
import ActivityHome from '../views/ActivityHome.vue'
import ActivityInfo from '../views/ActivityInfo.vue'

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
    path:"/register/todo",
    name:"RegisterTodo",
    component:RegisterTodo
  },
  {
    path:"/register/inquiry",
    name:"InquiryForm",
    component:InquiryForm
  },
  {
    path:"/user/info",
    name:"UserInfo",
    component:UserInfo
  },
  {
    path:"/register/activity",
    name:"ActivityHomw",
    component:ActivityHome
  },
  {
    path:"/view/activity",
    name:"ActivityInfo",
    component:ActivityInfo
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})


export default router