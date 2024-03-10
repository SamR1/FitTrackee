import {
  AuthUserActions,
  AuthUserGetters,
  AuthUserMutations,
} from '@/store/modules/authUser/enums'
import {
  NotificationsActions,
  NotificationsGetters,
  NotificationsMutations,
} from '@/store/modules/notifications/enums'
import {
  OAuth2Actions,
  OAuth2Getters,
  OAuth2Mutations,
} from '@/store/modules/oauth2/enums'
import {
  ReportsActions,
  ReportsGetters,
  ReportsMutations,
} from '@/store/modules/reports/enums'
import {
  RootActions,
  RootGetters,
  RootMutations,
} from '@/store/modules/root/enums'
import {
  SportsActions,
  SportsGetters,
  SportsMutation,
} from '@/store/modules/sports/enums'
import {
  StatisticsActions,
  StatisticsGetters,
  StatisticsMutations,
} from '@/store/modules/statistics/enums'
import {
  UsersActions,
  UsersGetters,
  UsersMutations,
} from '@/store/modules/users/enums'
import {
  WorkoutsActions,
  WorkoutsGetters,
  WorkoutsMutations,
} from '@/store/modules/workouts/enums'

export const ROOT_STORE = {
  ACTIONS: RootActions,
  GETTERS: RootGetters,
  MUTATIONS: RootMutations,
}

export const SPORTS_STORE = {
  ACTIONS: SportsActions,
  GETTERS: SportsGetters,
  MUTATIONS: SportsMutation,
}

export const STATS_STORE = {
  ACTIONS: StatisticsActions,
  GETTERS: StatisticsGetters,
  MUTATIONS: StatisticsMutations,
}

export const AUTH_USER_STORE = {
  ACTIONS: AuthUserActions,
  GETTERS: AuthUserGetters,
  MUTATIONS: AuthUserMutations,
}

export const OAUTH2_STORE = {
  ACTIONS: OAuth2Actions,
  GETTERS: OAuth2Getters,
  MUTATIONS: OAuth2Mutations,
}

export const NOTIFICATIONS_STORE = {
  ACTIONS: NotificationsActions,
  GETTERS: NotificationsGetters,
  MUTATIONS: NotificationsMutations,
}

export const REPORTS_STORE = {
  ACTIONS: ReportsActions,
  GETTERS: ReportsGetters,
  MUTATIONS: ReportsMutations,
}

export const USERS_STORE = {
  ACTIONS: UsersActions,
  GETTERS: UsersGetters,
  MUTATIONS: UsersMutations,
}

export const WORKOUTS_STORE = {
  ACTIONS: WorkoutsActions,
  GETTERS: WorkoutsGetters,
  MUTATIONS: WorkoutsMutations,
}
