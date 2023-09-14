import { capitalize } from 'vue'
import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router'

import AdminApplication from '@/components/Administration/AdminApplication.vue'
import AdminMenu from '@/components/Administration/AdminMenu.vue'
import AdminReport from '@/components/Administration/AdminReport.vue'
import AdminReports from '@/components/Administration/AdminReports.vue'
import AdminSports from '@/components/Administration/AdminSports.vue'
import AdminUsers from '@/components/Administration/AdminUsers.vue'
import Profile from '@/components/User/ProfileDisplay/index.vue'
import UserInfos from '@/components/User/ProfileDisplay/UserInfos.vue'
import UserPreferences from '@/components/User/ProfileDisplay/UserPreferences.vue'
import UsersList from '@/components/User/ProfileDisplay/UsersList.vue'
import ProfileEdition from '@/components/User/ProfileEdition/index.vue'
import UserAccountEdition from '@/components/User/ProfileEdition/UserAccountEdition.vue'
import UserInfosEdition from '@/components/User/ProfileEdition/UserInfosEdition.vue'
import UserPictureEdition from '@/components/User/ProfileEdition/UserPictureEdition.vue'
import UserPreferencesEdition from '@/components/User/ProfileEdition/UserPreferencesEdition.vue'
import UserPrivacyPolicyValidation from '@/components/User/ProfileEdition/UserPrivacyPolicyValidation.vue'
import AddUserApp from '@/components/User/UserApps/AddUserApp.vue'
import AuthorizeUserApp from '@/components/User/UserApps/AuthorizeUserApp.vue'
import UserApps from '@/components/User/UserApps/index.vue'
import UserApp from '@/components/User/UserApps/UserApp.vue'
import UserAppsList from '@/components/User/UserApps/UserAppsList.vue'
import UserRelationships from '@/components/User/UserRelationships.vue'
import UserSportPreferences from '@/components/User/UserSportPreferences.vue'
import createI18n from '@/i18n'
import store from '@/store'
import { AUTH_USER_STORE, NOTIFICATIONS_STORE } from '@/store/constants'
import AboutView from '@/views/AboutView.vue'
import Dashboard from '@/views/Dashboard.vue'
import NotFoundView from '@/views/NotFoundView.vue'
import PrivacyPolicyView from '@/views/PrivacyPolicyView.vue'
import LoginOrRegister from '@/views/user/LoginOrRegister.vue'

const { t } = createI18n.global

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
    meta: {
      title: 'dashboard.DASHBOARD',
    },
  },
  {
    path: '/login',
    name: 'Login',
    component: LoginOrRegister,
    props: { action: 'login' },
    meta: {
      title: 'user.LOGIN',
    },
  },
  {
    path: '/register',
    name: 'Register',
    component: LoginOrRegister,
    props: { action: 'register' },
    meta: {
      title: 'user.REGISTER',
    },
  },
  {
    path: '/account-confirmation',
    name: 'AccountConfirmation',
    component: () =>
      import(
        /* webpackChunkName: 'profile' */ '@/views/user/AccountConfirmationView.vue'
      ),
    meta: {
      title: 'user.ACCOUNT_CONFIRMATION',
    },
  },
  {
    path: '/account-confirmation/resend',
    name: 'AccountConfirmationResend',
    component: () =>
      import(
        /* webpackChunkName: 'reset' */ '@/views/user/AccountConfirmationResendView.vue'
      ),
    props: { action: 'account-confirmation-resend' },
    meta: {
      title: 'buttons.ACCOUNT-CONFIRMATION-RESEND',
    },
  },
  {
    path: '/account-confirmation/email-sent',
    name: 'AccountConfirmationEmailSend',
    component: () =>
      import(
        /* webpackChunkName: 'reset' */ '@/views/user/AccountConfirmationResendView.vue'
      ),
    props: { action: 'email-sent' },
    meta: {
      title: 'buttons.ACCOUNT-CONFIRMATION-RESEND',
    },
  },
  {
    path: '/password-reset/sent',
    name: 'PasswordEmailSent',
    component: () =>
      import(
        /* webpackChunkName: 'reset' */ '@/views/user/PasswordResetView.vue'
      ),
    props: { action: 'request-sent' },
    meta: {
      title: 'user.PASSWORD_RESET',
    },
  },
  {
    path: '/password-reset/request',
    name: 'PasswordResetRequest',
    component: () =>
      import(
        /* webpackChunkName: 'reset' */ '@/views/user/PasswordResetView.vue'
      ),
    props: { action: 'reset-request' },
    meta: {
      title: 'user.PASSWORD_RESET',
    },
  },
  {
    path: '/password-reset/password-updated',
    name: 'PasswordUpdated',
    component: () =>
      import(
        /* webpackChunkName: 'reset' */ '@/views/user/PasswordResetView.vue'
      ),
    props: { action: 'password-updated' },
    meta: {
      title: 'user.PASSWORD_RESET',
    },
  },
  {
    path: '/password-reset',
    name: 'PasswordReset',
    component: () =>
      import(
        /* webpackChunkName: 'reset' */ '@/views/user/PasswordResetView.vue'
      ),
    props: { action: 'reset' },
    meta: {
      title: 'user.PASSWORD_RESET',
    },
  },
  {
    path: '/email-update',
    name: 'EmailUpdate',
    component: () =>
      import(
        /* webpackChunkName: 'profile' */ '@/views/user/EmailUpdateView.vue'
      ),
    meta: {
      title: 'user.EMAIL_UPDATE',
    },
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
            meta: {
              title: 'user.PROFILE.TABS.PROFILE',
            },
          },
          {
            path: 'preferences',
            name: 'UserPreferences',
            component: UserPreferences,
            meta: {
              title: 'user.PROFILE.TABS.PREFERENCES',
            },
          },
          {
            path: 'sports',
            name: 'UserSportPreferences',
            component: UserSportPreferences,
            props: { isEdition: false },
            meta: {
              title: 'user.PROFILE.TABS.SPORTS',
            },
          },
          {
            path: 'apps',
            name: 'UserApps',
            component: UserApps,
            children: [
              {
                path: '',
                name: 'UserAppsList',
                component: UserAppsList,
                meta: {
                  title: 'user.PROFILE.TABS.APPS',
                },
              },
              {
                path: ':id',
                name: 'UserApp',
                component: UserApp,
                meta: {
                  title: 'user.PROFILE.TABS.APPS',
                },
              },
              {
                path: ':id/created',
                name: 'CreatedUserApp',
                component: UserApp,
                props: { afterCreation: true },
                meta: {
                  title: 'user.PROFILE.TABS.APPS',
                },
              },
              {
                path: 'new',
                name: 'AddUserApp',
                component: AddUserApp,
                meta: {
                  title: 'user.PROFILE.TABS.APPS',
                },
              },
              {
                path: 'authorize',
                name: 'AuthorizeUserApp',
                component: AuthorizeUserApp,
                meta: {
                  title: 'user.PROFILE.TABS.APPS',
                },
              },
            ],
          },
          {
            path: 'follow-requests',
            name: 'FollowRequests',
            component: UsersList,
            props: { itemType: 'follow-requests' },
          },
          {
            path: 'blocked-users',
            name: 'BlockedUsers',
            component: UsersList,
            props: { itemType: 'blocked-users' },
          },
          {
            path: 'followers',
            name: 'AuthUserFollowers',
            component: UserRelationships,
            props: { relationship: 'followers' },
          },
          {
            path: 'following',
            name: 'AuthUserFollowing',
            component: UserRelationships,
            props: { relationship: 'following' },
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
            meta: {
              title: 'user.PROFILE.EDIT',
            },
          },
          {
            path: 'account',
            name: 'UserAccountEdition',
            component: UserAccountEdition,
            meta: {
              title: 'user.PROFILE.ACCOUNT_EDITION',
            },
          },
          {
            path: 'picture',
            name: 'UserPictureEdition',
            component: UserPictureEdition,
            meta: {
              title: 'user.PROFILE.PICTURE_EDITION',
            },
          },
          {
            path: 'preferences',
            name: 'UserPreferencesEdition',
            component: UserPreferencesEdition,
            meta: {
              title: 'user.PROFILE.EDIT_PREFERENCES',
            },
          },
          {
            path: 'sports',
            name: 'UserSportPreferencesEdition',
            component: UserSportPreferences,
            props: { isEdition: true },
            meta: {
              title: 'user.PROFILE.EDIT_SPORTS_PREFERENCES',
            },
          },
          {
            path: 'privacy-policy',
            name: 'UserPrivacyPolicy',
            component: UserPrivacyPolicyValidation,
            meta: {
              title: 'user.PROFILE.PRIVACY-POLICY_EDITION',
            },
          },
        ],
      },
    ],
  },
  {
    path: '/notifications',
    name: 'Notifications',
    component: () =>
      import(
        /* webpackChunkName: 'notifications' */ '@/views/user/NotificationsView.vue'
      ),
  },
  {
    path: '/statistics',
    name: 'Statistics',
    component: () =>
      import(/* webpackChunkName: 'statistics' */ '@/views/StatisticsView.vue'),
    meta: {
      title: 'statistics.STATISTICS',
    },
  },
  {
    path: '/users',
    name: 'Users',
    component: () =>
      import(/* webpackChunkName: 'users' */ '@/views/UsersView.vue'),
  },
  {
    path: '/users/:username',
    name: 'User',
    props: { fromAdmin: false },
    component: () =>
      import(/* webpackChunkName: 'profile' */ '@/views/user/UserView.vue'),
    meta: {
      title: 'administration.USER',
    },
    children: [
      {
        path: 'followers',
        name: 'UserFollowers',
        component: UserRelationships,
        props: { relationship: 'followers' },
      },
      {
        path: 'following',
        name: 'UserFollowing',
        component: UserRelationships,
        props: { relationship: 'following' },
      },
    ],
  },
  {
    path: '/workouts',
    name: 'Workouts',
    component: () =>
      import(
        /* webpackChunkName: 'workouts' */ '@/views/workouts/WorkoutsView.vue'
      ),
    meta: {
      title: 'workouts.WORKOUT',
      count: 0,
    },
  },
  {
    path: '/workouts/:workoutId',
    name: 'Workout',
    component: () =>
      import(/* webpackChunkName: 'workouts' */ '@/views/workouts/Workout.vue'),
    props: { displaySegment: false },
    meta: {
      title: 'workouts.WORKOUT',
    },
  },
  {
    path: '/workouts/:workoutId/edit',
    name: 'EditWorkout',
    component: () =>
      import(
        /* webpackChunkName: 'workouts' */ '@/views/workouts/EditWorkout.vue'
      ),
    meta: {
      title: 'workouts.EDIT_WORKOUT',
    },
  },
  {
    path: '/workouts/:workoutId/segment/:segmentId',
    name: 'WorkoutSegment',
    component: () =>
      import(/* webpackChunkName: 'workouts' */ '@/views/workouts/Workout.vue'),
    props: { displaySegment: true },
    meta: {
      title: 'workouts.SEGMENT',
      count: 0,
    },
  },
  {
    path: '/workouts/:workoutId/comments/:commentId',
    name: 'WorkoutComment',
    component: () =>
      import(/* webpackChunkName: 'workouts' */ '@/views/workouts/Workout.vue'),
    props: { displaySegment: false },
  },
  {
    path: '/comments/:commentId',
    name: 'Comment',
    component: () =>
      import(
        /* webpackChunkName: 'workouts' */ '@/views/workouts/CommentView.vue'
      ),
  },
  {
    path: '/workouts/add',
    name: 'AddWorkout',
    component: () =>
      import(
        /* webpackChunkName: 'workouts' */ '@/views/workouts/AddWorkout.vue'
      ),
    meta: {
      title: 'workouts.ADD_WORKOUT',
    },
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
        meta: {
          title: 'admin.ADMINISTRATION',
        },
      },
      {
        path: 'application',
        name: 'ApplicationAdministration',
        component: AdminApplication,
        meta: {
          title: 'admin.APP_CONFIG.TITLE',
        },
      },
      {
        path: 'application/edit',
        name: 'ApplicationAdministrationEdition',
        component: AdminApplication,
        props: { edition: true },
        meta: {
          title: 'admin.APPLICATION',
        },
      },
      {
        path: 'sports',
        name: 'SportsAdministration',
        component: AdminSports,
        meta: {
          title: 'admin.SPORTS.TITLE',
        },
      },
      {
        path: 'reports',
        name: 'ReportsAdministration',
        component: AdminReports,
        meta: {
          title: 'admin.APP_MODERATION.TITLE',
        },
      },
      {
        path: 'reports/:reportId',
        name: 'ReportAdministration',
        component: AdminReport,
        meta: {
          title: 'admin.APP_MODERATION.REPORT',
        },
      },
      {
        path: 'users/:username',
        name: 'UserFromAdmin',
        component: () =>
          import(/* webpackChunkName: 'profile' */ '@/views/user/UserView.vue'),
        props: { fromAdmin: true },
        meta: {
          title: 'admin.USER',
          count: 1,
        },
      },
      {
        path: 'users',
        name: 'UsersAdministration',
        component: AdminUsers,
        meta: {
          title: 'admin.USERS.TITLE',
        },
      },
    ],
  },
  {
    path: '/about',
    name: 'About',
    component: AboutView,
    meta: {
      title: 'common.ABOUT',
    },
  },
  {
    path: '/privacy-policy',
    name: 'PrivacyPolicy',
    component: PrivacyPolicyView,
    meta: {
      title: 'privacy_policy.TITLE',
    },
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'not-found',
    component: NotFoundView,
    meta: {
      title: 'error.NOT_FOUND.PAGE',
    },
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
  '/account-confirmation',
  '/account-confirmation/resend',
  '/account-confirmation/email-sent',
]

const pathNamesWithoutChecks = [
  'EmailUpdate',
  'About',
  'User',
  'Workout',
  'PrivacyPolicy',
]

router.beforeEach((to, from, next) => {
  if ('title' in to.meta) {
    const title = typeof to.meta.title === 'string' ? to.meta.title : ''
    const translatedTitle = title
      ? typeof to.meta.count === 'number'
        ? t(title, +to.meta.count)
        : t(title)
      : ''
    window.document.title = `FitTrackee${
      title ? ` - ${capitalize(translatedTitle)}` : ''
    }`
  }
  store
    .dispatch(AUTH_USER_STORE.ACTIONS.CHECK_AUTH_USER)
    .then(() => {
      if (to.name && pathNamesWithoutChecks.includes(to.name.toString())) {
        return next()
      }

      if (store.getters[AUTH_USER_STORE.GETTERS.IS_AUTHENTICATED]) {
        store.dispatch(NOTIFICATIONS_STORE.ACTIONS.GET_UNREAD_STATUS)
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
