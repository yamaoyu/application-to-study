import { createRouter, createWebHistory } from 'vue-router'
import RegisterUser from '../views/RegisterUser.vue'
import LoginView from '../views/LoginForm.vue'
import UserHomeView from '../views/UserHome.vue'
import RegisterSalary from '../views/RegisterSalary.vue'
import MonthlyInfo from '../views/MonthlyInfo.vue'
import RegisterTodo from '../views/RegisterTodo.vue'
import InquiryForm from '../views/InquiryForm.vue'
import AllPeriodInfo from '../views/AllPeriodInfo.vue'
import EditTodo from '../views/EditTodo.vue'
import UserInfo from '../views/UserInfo.vue'
import YearInfo from '../views/YearInfo.vue'
import ActivityHome from '../views/ActivityHome.vue'

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
  },
  {
    path:"/user/info",
    name:"UserInfo",
    component:UserInfo
  },
  {
    path:"/view/year-activities",
    name:"YearInfo",
    component:YearInfo
  },
  {
    path:"/register/activity",
    name:"ActivityHomw",
    component:ActivityHome
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})


export default router