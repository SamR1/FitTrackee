<template>
  <div class="user-stats">
    <div class="user-stat">
      <span class="stat-number">{{ user.nb_workouts }}</span>
      <span class="stat-label">
        {{ $t('workouts.WORKOUT', user.nb_workouts) }}
      </span>
    </div>
    <div class="user-stat">
      <router-link
        v-if="displayLinks"
        :to="`/${getURL(user, authUser, $route.path)}/following`"
        class="stat-number"
      >
        {{ user.following }}
      </router-link>
      <span v-else class="stat-number">{{ user.following }}</span>
      <span class="stat-label">
        {{ $t('user.RELATIONSHIPS.FOLLOWING', user.following) }}
      </span>
    </div>
    <div class="user-stat">
      <router-link
        v-if="displayLinks"
        :to="`/${getURL(user, authUser, $route.path)}/followers`"
        class="stat-number"
      >
        {{ user.followers }}
      </router-link>
      <span v-else class="stat-number">{{ user.followers }}</span>
      <span class="stat-label">
        {{ $t('user.RELATIONSHIPS.FOLLOWER', user.followers) }}
      </span>
    </div>
  </div>
</template>

<script setup lang="ts">
  import { computed, toRefs } from 'vue'

  import useAuthUser from '@/composables/useAuthUser'
  import type { IAuthUserProfile, IUserLightProfile } from '@/types/user'

  interface Props {
    user: IUserLightProfile
  }
  const props = defineProps<Props>()
  const { user } = toRefs(props)

  const { authUser } = useAuthUser()

  const displayLinks = computed(() =>
    user.value.username === authUser?.value.username
      ? !authUser?.value.suspended_at
      : true
  )

  function getURL(
    user: IUserLightProfile,
    authUser: IAuthUserProfile,
    currentPath: string
  ): string {
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
