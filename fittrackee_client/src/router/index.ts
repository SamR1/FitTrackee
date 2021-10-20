import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router'

import store from '@/store'
import { USER_STORE } from '@/store/constants'
import AddWorkout from '@/views/AddWorkout.vue'
import Dashboard from '@/views/DashBoard.vue'
import LoginOrRegister from '@/views/LoginOrRegister.vue'
import NotFoundView from '@/views/NotFoundView.vue'
import PasswordResetView from '@/views/PasswordResetView.vue'
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
    props: { edition: false, tab: 'PROFILE' },
  },
  {
    path: '/password-reset/sent',
    name: 'PasswordEmailSent',
    component: PasswordResetView,
    props: { action: 'request-sent' },
  },
  {
    path: '/password-reset/request',
    name: 'PasswordResetRequest',
    component: PasswordResetView,
    props: { action: 'reset-request' },
  },
  {
    path: '/password-reset/password-updated',
    name: 'PasswordUpdated',
    component: PasswordResetView,
    props: { action: 'password-updated' },
  },
  {
    path: '/password-reset',
    name: 'PasswordReset',
    component: PasswordResetView,
    props: { action: 'reset' },
  },
  {
    path: '/profile/edit/picture',
    name: 'UserPictureEdition',
    component: ProfileView,
    props: { edition: true, tab: 'PICTURE' },
  },
  {
    path: '/profile/preferences',
    name: 'UserPreferences',
    component: ProfileView,
    props: { edition: false, tab: 'PREFERENCES' },
  },
  {
    path: '/profile/edit/preferences',
    name: 'UserPreferencesEdition',
    component: ProfileView,
    props: { edition: true, tab: 'PREFERENCES' },
  },
  {
    path: '/profile/edit',
    name: 'ProfileEdition',
    component: ProfileView,
    props: { edition: true, tab: 'PROFILE' },
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

const pathsWithoutAuthentication = [
  '/login',
  '/password-reset',
  '/password-reset/password-updated',
  '/password-reset/request',
  '/password-reset/sent',
  '/register',
]

router.beforeEach((to, from, next) => {
  store
    .dispatch(USER_STORE.ACTIONS.CHECK_AUTH_USER)
    .then(() => {
      if (
        store.getters[USER_STORE.GETTERS.IS_AUTHENTICATED] &&
        pathsWithoutAuthentication.includes(to.path)
      ) {
        return next('/')
      } else if (
        !store.getters[USER_STORE.GETTERS.IS_AUTHENTICATED] &&
        !pathsWithoutAuthentication.includes(to.path)
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
