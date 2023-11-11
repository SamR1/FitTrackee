<template>
  <div class="box user-header">
    <UserPicture :user="user" />
    <div class="user-details">
      <div class="user-name">{{ user.username }}</div>
      <div class="user-stats">
        <div class="user-stat">
          <span class="stat-number">{{ user.nb_workouts }}</span>
          <span class="stat-label">
            {{ $t('workouts.WORKOUT', user.nb_workouts) }}
          </span>
        </div>
        <div class="user-stat">
          <Distance
            :distance="user.total_distance"
            unitFrom="km"
            :digits="0"
            :displayUnit="false"
            :useImperialUnits="authUser.imperial_units"
          />
          <span class="stat-label">
            {{ authUser.imperial_units ? 'miles' : 'km' }}
          </span>
        </div>
        <div class="user-stat hide-small">
          <span class="stat-number">{{ user.nb_sports }}</span>
          <span class="stat-label">
            {{ $t('workouts.SPORT', user.nb_sports) }}
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
  import { computed, toRefs } from 'vue'
  import type { ComputedRef } from 'vue'

  import UserPicture from '@/components/User/UserPicture.vue'
  import { AUTH_USER_STORE } from '@/store/constants'
  import type { IAuthUserProfile, IUserProfile } from '@/types/user'
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
</script>

<style lang="scss" scoped>
  @import '~@/scss/vars.scss';

  .user-header {
    display: flex;
    align-items: stretch;

    .user-details {
      flex-grow: 1;
      padding: $default-padding;
      display: flex;
      flex-direction: column;
      align-items: center;

      .user-name {
        font-size: 2em;
        height: 60%;
      }

      .user-stats {
        display: flex;
        gap: $default-padding * 4;
        .user-stat {
          display: flex;
          flex-direction: column;
          align-items: center;
          padding-top: $default-padding;
          .stat-number,
          .stat-label {
            padding: 0 $default-padding * 0.5;
          }
          ::v-deep(.distance),
          .stat-number {
            font-weight: bold;
            font-size: 1.5em;
          }
        }
      }

      @media screen and (max-width: $x-small-limit) {
        .user-name {
          font-size: 1.5em;
        }

        .user-stats {
          gap: $default-padding * 2;
          .user-stat {
            ::v-deep(.distance),
            .stat-number {
              font-weight: bold;
              font-size: 1.2em;
            }

            &.hide-small {
              display: none;
            }
          }
        }
      }
    }
  }
</style>
