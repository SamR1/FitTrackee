import { capitalize } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'

import AdminApplication from '@/components/Administration/AdminApplication.vue'
import AdminEquipmentTypes from '@/components/Administration/AdminEquipmentTypes.vue'
import AdminMenu from '@/components/Administration/AdminMenu.vue'
import AdminQueuedTasksCount from '@/components/Administration/AdminQueuedTasksCount.vue'
import AdminQueuedTasksList from '@/components/Administration/AdminQueuedTasksList.vue'
import AdminReport from '@/components/Administration/AdminReport.vue'
import AdminReports from '@/components/Administration/AdminReports.vue'
import AdminSports from '@/components/Administration/AdminSports.vue'
import AdminUsers from '@/components/Administration/AdminUsers.vue'
import Profile from '@/components/User/ProfileDisplay/index.vue'
import UserInfos from '@/components/User/ProfileDisplay/UserInfos.vue'
import UserNotifications from '@/components/User/ProfileDisplay/UserNotifications.vue'
import UserPreferences from '@/components/User/ProfileDisplay/UserPreferences.vue'
import UsersList from '@/components/User/ProfileDisplay/UsersList.vue'
import ProfileEdition from '@/components/User/ProfileEdition/index.vue'
import UserAccountEdition from '@/components/User/ProfileEdition/UserAccountEdition.vue'
import UserInfosEdition from '@/components/User/ProfileEdition/UserInfosEdition.vue'
import UserNotificationsEdition from '@/components/User/ProfileEdition/UserNotificationsEdition.vue'
import UserPictureEdition from '@/components/User/ProfileEdition/UserPictureEdition.vue'
import UserPreferencesEdition from '@/components/User/ProfileEdition/UserPreferencesEdition.vue'
import UserPrivacyPolicyValidation from '@/components/User/ProfileEdition/UserPrivacyPolicyValidation.vue'
import UserAccountSuspension from '@/components/User/UserAccountSuspension.vue'
import AddUserApp from '@/components/User/UserApps/AddUserApp.vue'
import AuthorizeUserApp from '@/components/User/UserApps/AuthorizeUserApp.vue'
import UserApps from '@/components/User/UserApps/index.vue'
import UserApp from '@/components/User/UserApps/UserApp.vue'
import UserAppsList from '@/components/User/UserApps/UserAppsList.vue'
import UserArchiveUploads from '@/components/User/UserArchiveUploads/index.vue'
import UserArchiveUploadDetail from '@/components/User/UserArchiveUploads/UserArchiveUploadDetail.vue'
import UserArchiveUploadsList from '@/components/User/UserArchiveUploads/UserArchiveUploadsList.vue'
import EquipmentEdition from '@/components/User/UserEquipments/EquipmentEdition.vue'
import UserEquipments from '@/components/User/UserEquipments/index.vue'
import UserEquipment from '@/components/User/UserEquipments/UserEquipment.vue'
import UserEquipmentsList from '@/components/User/UserEquipments/UserEquipmentsList.vue'
import UserModeration from '@/components/User/UserModeration/index.vue'
import UserSanctionDetail from '@/components/User/UserModeration/UserSanctionDetail.vue'
import UserSanctionsList from '@/components/User/UserModeration/UserSanctionsList.vue'
import UserRelationships from '@/components/User/UserRelationships.vue'
import UserSports from '@/components/User/UserSports/index.vue'
import UserSport from '@/components/User/UserSports/UserSport.vue'
import UserSportEdition from '@/components/User/UserSports/UserSportEdition.vue'
import UserSportPreferences from '@/components/User/UserSports/UserSportPreferences.vue'
import createI18n from '@/i18n'
import store from '@/store'
import {
  AUTH_USER_STORE,
  NOTIFICATIONS_STORE,
  ROOT_STORE,
} from '@/store/constants'
import AboutView from '@/views/AboutView.vue'
import AdminView from '@/views/AdminView.vue'
import Dashboard from '@/views/Dashboard.vue'
import NotFoundView from '@/views/NotFoundView.vue'
import NotificationsView from '@/views/NotificationsView.vue'
import PrivacyPolicyView from '@/views/PrivacyPolicyView.vue'
import StatisticsView from '@/views/StatisticsView.vue'
import AccountConfirmationResendView from '@/views/user/AccountConfirmationResendView.vue'
import AccountConfirmationView from '@/views/user/AccountConfirmationView.vue'
import EmailUpdateView from '@/views/user/EmailUpdateView.vue'
import LoginOrRegister from '@/views/user/LoginOrRegister.vue'
import PasswordResetView from '@/views/user/PasswordResetView.vue'
import ProfileView from '@/views/user/ProfileView.vue'
import UserView from '@/views/user/UserView.vue'
import UsersView from '@/views/UsersView.vue'
import AddWorkout from '@/views/workouts/AddWorkout.vue'
import CommentView from '@/views/workouts/CommentView.vue'
import EditWorkout from '@/views/workouts/EditWorkout.vue'
import Likes from '@/views/workouts/Likes.vue'
import Workout from '@/views/workouts/Workout.vue'
import WorkoutsView from '@/views/workouts/WorkoutsView.vue'

const { t } = createI18n.global

const getTabFromPath = (path: string): string => {
  const regex = /(\/profile)(\/edit)*(\/*)/
  const tab = path.replace(regex, '').toUpperCase()
  return tab === '' ? 'PROFILE' : tab.split('/')[0].toUpperCase()
}

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'Dashboard',
    component: Dashboard,
    meta: {
      title: 'dashboard.DASHBOARD',
      allowedToSuspendedUser: false,
    },
  },
  {
    path: '/login',
    name: 'Login',
    component: LoginOrRegister,
    props: { action: 'login' },
    meta: {
      title: 'user.LOGIN',
      withoutAuth: true,
    },
  },
  {
    path: '/register',
    name: 'Register',
    component: LoginOrRegister,
    props: { action: 'register' },
    meta: {
      title: 'user.REGISTER',
      withoutAuth: true,
    },
  },
  {
    path: '/account-confirmation',
    name: 'AccountConfirmation',
    component: AccountConfirmationView,
    meta: {
      title: 'user.ACCOUNT_CONFIRMATION',
      withoutAuth: true,
    },
  },
  {
    path: '/account-confirmation/resend',
    name: 'AccountConfirmationResend',
    component: AccountConfirmationResendView,
    props: { action: 'account-confirmation-resend' },
    meta: {
      title: 'buttons.ACCOUNT-CONFIRMATION-RESEND',
      withoutAuth: true,
    },
  },
  {
    path: '/account-confirmation/email-sent',
    name: 'AccountConfirmationEmailSend',
    component: AccountConfirmationResendView,
    props: { action: 'email-sent' },
    meta: {
      title: 'buttons.ACCOUNT-CONFIRMATION-RESEND',
      withoutAuth: true,
    },
  },
  {
    path: '/password-reset/sent',
    name: 'PasswordEmailSent',
    component: PasswordResetView,
    props: { action: 'request-sent' },
    meta: {
      title: 'user.PASSWORD_RESET',
      withoutAuth: true,
    },
  },
  {
    path: '/password-reset/request',
    name: 'PasswordResetRequest',
    component: PasswordResetView,
    props: { action: 'reset-request' },
    meta: {
      title: 'user.PASSWORD_RESET',
      withoutAuth: true,
    },
  },
  {
    path: '/password-reset/password-updated',
    name: 'PasswordUpdated',
    component: PasswordResetView,
    props: { action: 'password-updated' },
    meta: {
      title: 'user.PASSWORD_RESET',
      withoutAuth: true,
    },
  },
  {
    path: '/password-reset',
    name: 'PasswordReset',
    component: PasswordResetView,
    props: { action: 'reset' },
    meta: {
      title: 'user.PASSWORD_RESET',
      withoutAuth: true,
    },
  },
  {
    path: '/email-update',
    name: 'EmailUpdate',
    component: EmailUpdateView,
    meta: {
      title: 'user.EMAIL_UPDATE',
      withoutChecks: true,
    },
  },
  {
    path: '/profile',
    name: 'Profile',
    component: ProfileView,
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
            path: 'notifications',
            name: 'UserNotifications',
            component: UserNotifications,
            meta: {
              title: 'user.PROFILE.TABS.NOTIFICATIONS',
            },
          },
          {
            path: 'sports',
            name: 'UserSports',
            component: UserSports,
            props: { isEdition: false },
            meta: {
              title: 'user.PROFILE.TABS.SPORTS',
            },
            children: [
              {
                path: '',
                name: 'UserSportPreferences',
                component: UserSportPreferences,
                meta: {
                  title: 'user.PROFILE.TABS.SPORTS',
                },
              },
              {
                path: ':id',
                name: 'UserSport',
                component: UserSport,
                meta: {
                  title: 'user.PROFILE.TABS.SPORTS',
                },
              },
            ],
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
            path: 'equipments',
            name: 'UserEquipments',
            component: UserEquipments,
            props: { isEdition: false },
            children: [
              {
                path: '',
                name: 'UserEquipmentsList',
                component: UserEquipmentsList,
                meta: {
                  title: 'user.PROFILE.TABS.EQUIPMENTS',
                },
              },
              {
                path: 'new',
                name: 'AddEquipment',
                component: EquipmentEdition,
                meta: {
                  title: 'user.PROFILE.TABS.EQUIPMENTS',
                },
              },
              {
                path: ':id',
                name: 'Equipment',
                component: UserEquipment,
                meta: {
                  title: 'user.PROFILE.TABS.EQUIPMENTS',
                },
              },
            ],
          },
          {
            path: 'follow-requests',
            name: 'FollowRequests',
            component: UsersList,
            props: { itemType: 'follow-requests' },
            meta: {
              title: 'user.PROFILE.TABS.FOLLOW-REQUESTS',
            },
          },
          {
            path: 'blocked-users',
            name: 'BlockedUsers',
            component: UsersList,
            props: { itemType: 'blocked-users' },
            meta: {
              title: 'user.PROFILE.TABS.BLOCKED-USERS',
            },
          },
          {
            path: 'followers',
            name: 'AuthUserFollowers',
            component: UserRelationships,
            props: { relationship: 'followers' },
            meta: {
              title: 'user.RELATIONSHIPS.FOLLOWER',
              count: 0,
            },
          },
          {
            path: 'following',
            name: 'AuthUserFollowing',
            component: UserRelationships,
            props: { relationship: 'following' },
            meta: {
              title: 'user.RELATIONSHIPS.FOLLOWING',
              count: 0,
            },
          },
          {
            path: 'suspension',
            name: 'AuthUserAccountSuspension',
            component: UserAccountSuspension,
          },
          {
            path: 'moderation',
            name: 'Moderation',
            component: UserModeration,
            meta: {
              title: 'user.PROFILE.TABS.MODERATION',
            },
            children: [
              {
                path: '',
                name: 'UserSanctionList',
                component: UserSanctionsList,
              },
              {
                path: 'sanctions/:action_id',
                name: 'UserSanctionDetail',
                component: UserSanctionDetail,
              },
            ],
          },
          {
            path: 'archive-uploads',
            name: 'UserArchiveUploads',
            component: UserArchiveUploads,
            children: [
              {
                path: '',
                name: 'UserArchiveUploadsList',
                component: UserArchiveUploadsList,
                meta: {
                  title: 'user.PROFILE.TABS.ARCHIVE-UPLOADS',
                },
              },
              {
                path: ':task_id',
                name: 'UserArchiveUploadDetail',
                component: UserArchiveUploadDetail,
                meta: {
                  title: 'user.PROFILE.TABS.ARCHIVE-UPLOADS',
                },
              },
            ],
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
            path: 'notifications',
            name: 'UserNotificationsEdition',
            component: UserNotificationsEdition,
            meta: {
              title: 'user.PROFILE.EDIT_NOTIFICATIONS',
            },
          },
          {
            path: 'sports',
            name: 'UserSportsEdition',
            component: UserSports,
            props: { isEdition: true },
            meta: {
              title: 'user.PROFILE.EDIT_SPORTS_PREFERENCES',
            },
            children: [
              {
                path: '',
                name: 'UserSportPreferencesEdition',
                component: UserSportPreferences,
                meta: {
                  title: 'user.PROFILE.TABS.SPORTS',
                },
              },
              {
                path: ':id',
                name: 'UserSportEdition',
                component: UserSportEdition,
                meta: {
                  title: 'user.PROFILE.TABS.SPORTS',
                },
              },
            ],
          },
          {
            path: 'equipments',
            name: 'UserEquipmentsEdition',
            component: UserEquipments,
            props: { isEdition: true },
            children: [
              {
                path: '',
                name: 'UserEquipmentsListEdition',
                component: UserEquipmentsList,
                meta: {
                  title: 'user.PROFILE.TABS.EQUIPMENTS',
                },
              },
              {
                path: ':id',
                name: 'EquipmentEdition',
                component: EquipmentEdition,
                meta: {
                  title: 'user.PROFILE.TABS.EQUIPMENTS',
                },
              },
            ],
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
    component: NotificationsView,
    meta: {
      allowedToSuspendedUser: false,
    },
  },
  {
    path: '/statistics',
    name: 'Statistics',
    component: StatisticsView,
    meta: {
      title: 'statistics.STATISTICS',
      allowedToSuspendedUser: false,
    },
  },
  {
    path: '/users',
    name: 'Users',
    component: UsersView,
    meta: {
      allowedToSuspendedUser: false,
    },
  },
  {
    path: '/users/:username',
    name: 'User',
    props: { fromAdmin: false },
    component: UserView,
    meta: {
      title: 'user.USER',
      withoutChecks: true,
      allowedToSuspendedUser: false,
    },
    children: [
      {
        path: 'followers',
        name: 'UserFollowers',
        component: UserRelationships,
        props: { relationship: 'followers' },
        meta: {
          withoutAuth: false,
          withoutChecks: false,
        },
      },
      {
        path: 'following',
        name: 'UserFollowing',
        component: UserRelationships,
        props: { relationship: 'following' },
        meta: {
          withoutAuth: false,
          withoutChecks: false,
        },
      },
    ],
  },
  {
    path: '/workouts',
    name: 'Workouts',
    component: WorkoutsView,
    meta: {
      title: 'workouts.WORKOUT',
      count: 0,
      allowedToSuspendedUser: false,
    },
  },
  {
    path: '/workouts/:workoutId',
    name: 'Workout',
    component: Workout,
    props: { displaySegment: false },
    meta: {
      title: 'workouts.WORKOUT',
      withoutChecks: true,
      allowedToSuspendedUser: false,
    },
  },
  {
    path: '/workouts/:workoutId/likes',
    name: 'WorkoutLikes',
    component: Likes,
    props: { objectType: 'workout' },
    meta: {
      title: 'workouts.LIKES',
      withoutChecks: true,
      allowedToSuspendedUser: false,
    },
  },
  {
    path: '/workouts/:workoutId/edit',
    name: 'EditWorkout',
    component: EditWorkout,
    meta: {
      title: 'workouts.EDIT_WORKOUT',
      allowedToSuspendedUser: false,
    },
  },
  {
    path: '/workouts/:workoutId/segment/:segmentId',
    name: 'WorkoutSegment',
    component: Workout,
    props: { displaySegment: true },
    meta: {
      title: 'workouts.SEGMENT',
      count: 0,
      withoutChecks: true,
      allowedToSuspendedUser: false,
    },
  },
  {
    path: '/workouts/:workoutId/comments/:commentId',
    name: 'WorkoutComment',
    component: Workout,
    props: { displaySegment: false },
    meta: {
      allowedToSuspendedUser: false,
      withoutChecks: true,
    },
  },
  {
    path: '/workouts/:workoutId/comments/:commentId/likes',
    name: 'WorkoutCommentLikes',
    component: Likes,
    props: { objectType: 'comment' },
    meta: {
      title: 'workouts.LIKES',
      withoutChecks: true,
      allowedToSuspendedUser: false,
    },
  },
  {
    path: '/comments/:commentId',
    name: 'Comment',
    component: CommentView,
    meta: {
      allowedToSuspendedUser: false,
      withoutChecks: true,
    },
  },
  {
    path: '/comments/:commentId/likes',
    name: 'CommentLikes',
    component: Likes,
    props: { objectType: 'comment' },
    meta: {
      title: 'workouts.LIKES',
      withoutChecks: true,
      allowedToSuspendedUser: false,
    },
  },
  {
    path: '/workouts/add',
    name: 'AddWorkout',
    component: AddWorkout,
    meta: {
      title: 'workouts.ADD_WORKOUT',
      allowedToSuspendedUser: false,
    },
  },
  {
    path: '/admin',
    name: 'Administration',
    component: AdminView,
    meta: {
      allowedToSuspendedUser: false,
      minimumRole: 'moderator',
    },
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
          minimumRole: 'admin',
        },
      },
      {
        path: 'application/edit',
        name: 'ApplicationAdministrationEdition',
        component: AdminApplication,
        props: { edition: true },
        meta: {
          title: 'admin.APPLICATION',
          minimumRole: 'admin',
        },
      },
      {
        path: 'equipment-types',
        name: 'EquipmentTypeAdministration',
        component: AdminEquipmentTypes,
        meta: {
          title: 'admin.EQUIPMENT_TYPES.TITLE',
          minimumRole: 'admin',
        },
      },
      {
        path: 'sports',
        name: 'SportsAdministration',
        component: AdminSports,
        meta: {
          title: 'admin.SPORTS.TITLE',
          minimumRole: 'admin',
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
        component: UserView,
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
          minimumRole: 'admin',
        },
      },
      {
        path: 'queued-tasks',
        name: 'QueuedTasksCountAdministration',
        component: AdminQueuedTasksCount,
        meta: {
          title: 'admin.USERS_QUEUED_TASKS.LABEL',
          minimumRole: 'admin',
        },
      },
      {
        path: 'queued-tasks/:taskType',
        name: 'QueuedTaskListAdministration',
        component: AdminQueuedTasksList,
        meta: {
          title: 'admin.USERS_QUEUED_TASKS.LABEL',
          minimumRole: 'admin',
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
      withoutChecks: true,
    },
  },
  {
    path: '/privacy-policy',
    name: 'PrivacyPolicy',
    component: PrivacyPolicyView,
    meta: {
      title: 'privacy_policy.TITLE',
      withoutChecks: true,
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
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
})

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
  store.commit(ROOT_STORE.MUTATIONS.EMPTY_ERROR_MESSAGES)
  store
    .dispatch(AUTH_USER_STORE.ACTIONS.CHECK_AUTH_USER)
    .then(() => {
      if (to.meta.withoutChecks) {
        return next()
      }

      if (
        store.getters[AUTH_USER_STORE.GETTERS.IS_PROFILE_LOADED] &&
        store.getters[AUTH_USER_STORE.GETTERS.IS_SUSPENDED] &&
        !to.path.startsWith('/profile') &&
        !to.meta.allowedToSuspendedUser
      ) {
        return next('/profile')
      }

      if (
        store.getters[AUTH_USER_STORE.GETTERS.IS_AUTHENTICATED] &&
        store.getters[AUTH_USER_STORE.GETTERS.IS_PROFILE_LOADED] &&
        !store.getters[AUTH_USER_STORE.GETTERS.IS_SUSPENDED]
      ) {
        store.dispatch(NOTIFICATIONS_STORE.ACTIONS.GET_UNREAD_STATUS)
      }

      if (
        store.getters[AUTH_USER_STORE.GETTERS.IS_AUTHENTICATED] &&
        to.meta.withoutAuth
      ) {
        return next('/')
      }

      if (
        !store.getters[AUTH_USER_STORE.GETTERS.IS_AUTHENTICATED] &&
        !to.meta.withoutAuth
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
