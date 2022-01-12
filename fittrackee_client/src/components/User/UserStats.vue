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
      <span class="stat-number">{{ user.following }}</span>
      <span class="stat-label">
        {{ $t('user.RELATIONSHIPS.FOLLOWING', user.following) }}
      </span>
    </div>
    <div class="user-stat">
      <span class="stat-number">{{ user.followers }}</span>
      <span class="stat-label">
        {{ $t('user.RELATIONSHIPS.FOLLOWER', user.followers) }}
      </span>
    </div>
  </div>
</template>

<script setup lang="ts">
  import { toRefs } from 'vue'

  import { IAuthUserProfile, IUserProfile } from '@/types/user'

  interface Props {
    authUser: IAuthUserProfile
    user: IUserProfile
  }
  const props = defineProps<Props>()

  const { authUser, user } = toRefs(props)
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
  }
</style>
