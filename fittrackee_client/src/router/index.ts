import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router'

import store from '@/store'
import { USER_STORE } from '@/store/constants'
import AddWorkout from '@/views/AddWorkout.vue'
import Dashboard from '@/views/DashBoard.vue'
import LoginOrRegister from '@/views/LoginOrRegister.vue'
import NotFoundView from '@/views/NotFoundView.vue'
import ProfileView from '@/views/ProfileView.vue'
import StatisticsView from '@/views/StatisticsView.vue'
import EditWorkout from '@/views/workouts/EditWorkout.vue'
import Workout from '@/views/workouts/Workout.vue'
import Workouts from '@/views/workouts/WorkoutsView.vue'

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
  {
    path: '/profile',
    name: 'Profile',
    component: ProfileView,
    props: { edition: false },
  },
  {
    path: '/profile/edit',
    name: 'ProfileEdition',
    component: ProfileView,
    props: { edition: true },
  },
  {
    path: '/statistics',
    name: 'Statistics',
    component: StatisticsView,
  },
  {
    path: '/workouts',
    name: 'Workouts',
    component: Workouts,
  },
  {
    path: '/workouts/:workoutId',
    name: 'Workout',
    component: Workout,
    props: { displaySegment: false },
  },
  {
    path: '/workouts/:workoutId/edit',
    name: 'EditWorkout',
    component: EditWorkout,
  },
  {
    path: '/workouts/:workoutId/segment/:segmentId',
    name: 'WorkoutSegment',
    component: Workout,
    props: { displaySegment: true },
  },
  {
    path: '/workouts/add',
    name: 'AddWorkout',
    component: AddWorkout,
  },
  { path: '/:pathMatch(.*)*', name: 'not-found', component: NotFoundView },
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
