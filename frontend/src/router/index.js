import { createRouter, createWebHistory } from 'vue-router'
import SignIn from '@/components/login_register_page/SignIn.vue'
import SignUp from '@/components/login_register_page/SignUp.vue'
import HomePage from '@/components/home_page/HomePage.vue'
import { useAuth } from '@/composables/useAuth'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/login',    component: SignIn },
    { path: '/register', component: SignUp },
    { path: '/home',     component: HomePage },
    { path: '/',         redirect: '/login' }
  ]
})

router.beforeEach((to, from, next) => {
  const { isAuthenticated, restoreSession } = useAuth()
  restoreSession()
  
  if (to.path === '/home' && !isAuthenticated.value) {
    next('/login')
  } else if ((to.path === '/login' || to.path === '/register') && isAuthenticated.value) {
    next('/home')
  } else {
    next()
  }
})

export default router