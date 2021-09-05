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
  UserActions,
  UserGetters,
  UserMutations,
} from '@/store/modules/user/enums'
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

export const USER_STORE = {
  ACTIONS: UserActions,
  GETTERS: UserGetters,
  MUTATIONS: UserMutations,
}

export const WORKOUTS_STORE = {
  ACTIONS: WorkoutsActions,
  GETTERS: WorkoutsGetters,
  MUTATIONS: WorkoutsMutations,
}
