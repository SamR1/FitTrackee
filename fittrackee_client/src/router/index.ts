import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router'

import store from '@/store'
import { USER_STORE } from '@/store/constants'
import Dashboard from '@/views/DashBoard.vue'
import LoginOrRegister from '@/views/LoginOrRegister.vue'
import NotFound from '@/views/NotFound.vue'

const routes: Array<RouteRecordRaw> = [
  {
    path: '/',
    name: 'Dashboard',
    component: Dashboard,
  },
  {
    path: '/login',
    name: 'Login',
    component: LoginOrRegister,
    props: { action: 'login' },
  },
  {
    path: '/register',
    name: 'Register',
    component: LoginOrRegister,
    props: { action: 'register' },
  },
  { path: '/:pathMatch(.*)*', name: 'not-found', component: NotFound },
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes,
})

router.beforeEach((to, from, next) => {
  store
    .dispatch(USER_STORE.ACTIONS.CHECK_AUTH_USER)
    .then(() => {
      if (
        store.getters[USER_STORE.GETTERS.IS_AUTHENTICATED] &&
        ['/login', '/register'].includes(to.path)
      ) {
        return next('/')
      } else if (
        !store.getters[USER_STORE.GETTERS.IS_AUTHENTICATED] &&
        !['/login', '/register'].includes(to.path)
      ) {
        const path =
          to.path === '/'
            ? { path: '/login' }
            : { path: '/login', query: { from: to.fullPath } }
        next(path)
      } else {
        next()
      }
    })
    .catch((error) => {
      console.error(error)
      next()
    })
})

export default router
