<template>
  <div class="user-stats">
    <div class="user-stat">
      <span class="stat-number">{{ user.nb_workouts }}</span>
      <span class="stat-label">
        {{ $t('workouts.WORKOUT', user.nb_workouts) }}
      </span>
    </div>
    <div class="user-stat" v-if="'total_distance' in user">
      <Distance
        :distance="user.total_distance"
        unitFrom="km"
        :digits="0"
        :displayUnit="false"
        :useImperialUnits="authUser ? authUser.imperial_units : false"
      />
      <span class="stat-label">
        {{ user.imperial_units ? 'miles' : 'km' }}
      </span>
    </div>
    <div class="user-stat" v-if="'nb_sports' in user">
      <span class="stat-number">{{ user.nb_sports }}</span>
      <span class="stat-label">
        {{ $t('workouts.SPORT', user.nb_sports) }}
      </span>
    </div>
    <div class="user-stat">
      <router-link
        :to="`/${getURL(user, authUser, $route.path)}/following`"
        class="stat-number"
      >
        {{ user.following }}
      </router-link>
      <span class="stat-label">
        {{ $t('user.RELATIONSHIPS.FOLLOWING', user.following) }}
      </span>
    </div>
    <div class="user-stat">
      <router-link
        :to="`/${getURL(user, authUser, $route.path)}/followers`"
        class="stat-number"
      >
        {{ user.followers }}
      </router-link>
      <span class="stat-label">
        {{ $t('user.RELATIONSHIPS.FOLLOWER', user.followers) }}
      </span>
    </div>
  </div>
</template>

<script setup lang="ts">
  import { ComputedRef, computed, toRefs } from 'vue'

  import { AUTH_USER_STORE } from '@/store/constants'
  import { IAuthUserProfile, IUserProfile } from '@/types/user'
  import { useStore } from '@/use/useStore'

  interface Props {
    user: IUserProfile
  }
  const props = defineProps<Props>()

  const { user } = toRefs(props)
  const store = useStore()
  const authUser: ComputedRef<IAuthUserProfile> = computed(
    () => store.getters[AUTH_USER_STORE.GETTERS.AUTH_USER_PROFILE]
  )
  function getURL(
    user: IUserProfile,
    authUser: IAuthUserProfile,
    currentPath: string
  ) {
    return user.username === authUser?.username &&
      currentPath.includes('/profile')
      ? 'profile'
      : `users/${user.username}`
  }
</script>

<style lang="scss" scoped>
  @import '~@/scss/vars.scss';

  .user-stats {
    display: flex;
    .user-stat {
      display: flex;
      .stat-number,
      .stat-label {
        padding: 0 $default-padding * 0.5;
      }
      ::v-deep(.distance),
      .stat-number {
        font-weight: bold;
      }
    }

    .router-link-exact-active {
      text-decoration: underline;
    }
  }
</style>
