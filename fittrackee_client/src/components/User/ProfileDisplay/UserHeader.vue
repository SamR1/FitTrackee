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
          <span class="stat-number">{{
            Number(user.total_distance).toFixed(0)
          }}</span>
          <span class="stat-label">km</span>
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
  import { toRefs } from 'vue'

  import UserPicture from '@/components/User/UserPicture.vue'
  import { IUserProfile } from '@/types/user'

  interface Props {
    user: IUserProfile
  }
  const props = defineProps<Props>()

  const { user } = toRefs(props)
</script>

<style lang="scss" scoped>
  @import '~@/scss/base.scss';

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
