import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router'

import AdminApplication from '@/components/Administration/AdminApplication.vue'
import AdminMenu from '@/components/Administration/AdminMenu.vue'
import AdminSports from '@/components/Administration/AdminSports.vue'
import AdminUsers from '@/components/Administration/AdminUsers.vue'
import Profile from '@/components/User/ProfileDisplay/index.vue'
import UserInfos from '@/components/User/ProfileDisplay/UserInfos.vue'
import UserPreferences from '@/components/User/ProfileDisplay/UserPreferences.vue'
import ProfileEdition from '@/components/User/ProfileEdition/index.vue'
import UserInfosEdition from '@/components/User/ProfileEdition/UserInfosEdition.vue'
import UserPictureEdition from '@/components/User/ProfileEdition/UserPictureEdition.vue'
import UserPreferencesEdition from '@/components/User/ProfileEdition/UserPreferencesEdition.vue'
import UserSportPreferences from '@/components/User/UserSportPreferences.vue'
import store from '@/store'
import { AUTH_USER_STORE } from '@/store/constants'
import Dashboard from '@/views/Dashboard.vue'
import NotFoundView from '@/views/NotFoundView.vue'
import LoginOrRegister from '@/views/user/LoginOrRegister.vue'

const getTabFromPath = (path: string): string => {
  const regex = /(\/profile)(\/edit)*(\/*)/
  const tag = path.replace(regex, '').toUpperCase()
  return tag === '' ? 'PROFILE' : tag.toUpperCase()
}

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
    path: '/password-reset/sent',
    name: 'PasswordEmailSent',
    component: () =>
      import(
        /* webpackChunkName: 'reset' */ '@/views/user/PasswordResetView.vue'
      ),
    props: { action: 'request-sent' },
  },
  {
    path: '/password-reset/request',
    name: 'PasswordResetRequest',
    component: () =>
      import(
        /* webpackChunkName: 'reset' */ '@/views/user/PasswordResetView.vue'
      ),
    props: { action: 'reset-request' },
  },
  {
    path: '/password-reset/password-updated',
    name: 'PasswordUpdated',
    component: () =>
      import(
        /* webpackChunkName: 'reset' */ '@/views/user/PasswordResetView.vue'
      ),
    props: { action: 'password-updated' },
  },
  {
    path: '/password-reset',
    name: 'PasswordReset',
    component: () =>
      import(
        /* webpackChunkName: 'reset' */ '@/views/user/PasswordResetView.vue'
      ),
    props: { action: 'reset' },
  },
  {
    path: '/profile',
    name: 'Profile',
    component: () =>
      import(/* webpackChunkName: 'profile' */ '@/views/user/ProfileView.vue'),
    children: [
      {
        path: '',
        name: 'UserProfile',
        component: Profile,
        props: (route) => ({
          tab: getTabFromPath(route.path),
        }),
        children: [
          {
            path: '',
            name: 'UserInfos',
            component: UserInfos,
          },
          {
            path: 'preferences',
            name: 'UserPreferences',
            component: UserPreferences,
          },
          {
            path: 'sports',
            name: 'UserSportPreferences',
            component: UserSportPreferences,
            props: { isEdition: false },
          },
        ],
      },
      {
        path: 'edit',
        name: 'UserProfileEdition',
        component: ProfileEdition,
        props: (route) => ({
          tab: getTabFromPath(route.path),
        }),
        children: [
          {
            path: '',
            name: 'UserInfosEdition',
            component: UserInfosEdition,
          },
          {
            path: 'picture',
            name: 'UserPictureEdition',
            component: UserPictureEdition,
          },
          {
            path: 'preferences',
            name: 'UserPreferencesEdition',
            component: UserPreferencesEdition,
          },
          {
            path: 'sports',
            name: 'UserSportPreferencesEdition',
            component: UserSportPreferences,
            props: { isEdition: true },
          },
        ],
      },
    ],
  },
  {
    path: '/statistics',
    name: 'Statistics',
    component: () =>
      import(/* webpackChunkName: 'statistics' */ '@/views/StatisticsView.vue'),
  },
  {
    path: '/users/:username',
    name: 'User',
    component: () =>
      import(/* webpackChunkName: 'profile' */ '@/views/user/UserView.vue'),
  },
  {
    path: '/workouts',
    name: 'Workouts',
    component: () =>
      import(
        /* webpackChunkName: 'workouts' */ '@/views/workouts/WorkoutsView.vue'
      ),
  },
  {
    path: '/workouts/:workoutId',
    name: 'Workout',
    component: () =>
      import(/* webpackChunkName: 'workouts' */ '@/views/workouts/Workout.vue'),
    props: { displaySegment: false },
  },
  {
    path: '/workouts/:workoutId/edit',
    name: 'EditWorkout',
    component: () =>
      import(
        /* webpackChunkName: 'workouts' */ '@/views/workouts/EditWorkout.vue'
      ),
  },
  {
    path: '/workouts/:workoutId/segment/:segmentId',
    name: 'WorkoutSegment',
    component: () =>
      import(/* webpackChunkName: 'workouts' */ '@/views/workouts/Workout.vue'),
    props: { displaySegment: true },
  },
  {
    path: '/workouts/add',
    name: 'AddWorkout',
    component: () =>
      import(
        /* webpackChunkName: 'workouts' */ '@/views/workouts/AddWorkout.vue'
      ),
  },
  {
    path: '/admin',
    name: 'Administration',
    component: () =>
      import(/* webpackChunkName: 'admin' */ '@/views/AdminView.vue'),
    children: [
      {
        path: '',
        name: 'AdministrationMenu',
        component: AdminMenu,
      },
      {
        path: 'application',
        name: 'ApplicationAdministration',
        component: AdminApplication,
      },
      {
        path: 'application/edit',
        name: 'ApplicationAdministrationEdition',
        component: AdminApplication,
        props: { edition: true },
      },
      {
        path: 'sports',
        name: 'SportsAdministration',
        component: AdminSports,
      },
      {
        path: 'users',
        name: 'UsersAdministration',
        component: AdminUsers,
      },
    ],
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'not-found',
    component: NotFoundView,
  },
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
    .dispatch(AUTH_USER_STORE.ACTIONS.CHECK_AUTH_USER)
    .then(() => {
      if (to.path.startsWith('/users')) {
        return next()
      }

      if (
        store.getters[AUTH_USER_STORE.GETTERS.IS_AUTHENTICATED] &&
        pathsWithoutAuthentication.includes(to.path)
      ) {
        return next('/')
      }

      if (
        !store.getters[AUTH_USER_STORE.GETTERS.IS_AUTHENTICATED] &&
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
