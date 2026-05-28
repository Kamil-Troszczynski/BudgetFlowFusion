import { createRouter, createWebHistory } from 'vue-router'
import SignIn from '@/components/auth/SignIn.vue'
import SignUp from '@/components/auth/SignUp.vue'


const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/login',    component: SignIn },
    { path: '/register', component: SignUp },
    { path: '/',         redirect: '/login' }
  ]
})

export default router