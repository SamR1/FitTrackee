<template>
  <div class="box user-header">
    <div class="follows-you" v-if="user.follows === 'true'">
      {{ $t('user.RELATIONSHIPS.FOLLOWS_YOU') }}
    </div>
    <UserPicture :user="user" />
    <div class="user-details">
      <div class="user-name">{{ user.username }}</div>
      <a
        class="remote-user-account"
        v-if="user.is_remote"
        :href="user.profile_link"
        target="_blank"
      >
        {{ user.fullname }}
      </a>
      <UserStats :user="user" />
    </div>
  </div>
</template>

<script setup lang="ts">
  import { toRefs } from 'vue'

  import UserPicture from '@/components/User/UserPicture.vue'
  import UserStats from '@/components/User/UserStats.vue'
  import { IAuthUserProfile, IUserProfile } from '@/types/user'

  interface Props {
    user: IUserProfile
    authUser?: IAuthUserProfile
  }
  const props = defineProps<Props>()

  const { user } = toRefs(props)
</script>

<style lang="scss" scoped>
  @import '~@/scss/vars.scss';

  .user-header {
    display: flex;
    align-items: stretch;
    position: relative;

    .follows-you {
      position: absolute;
      margin-top: -$default-margin;
      margin-left: -$default-margin;
    }

    ::v-deep(.user-picture) {
      min-width: 20%;
    }

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

      ::v-deep(.user-stats) {
        flex-wrap: nowrap;
        gap: $default-padding * 4;
        .user-stat {
          flex-direction: column;
          align-items: center;
          padding-top: $default-padding;

          .distance,
          .stat-number {
            font-size: 1.5em;
          }
        }
      }
    }

    @media screen and (max-width: $small-limit) {
      .user-details {
        .user-name {
          font-size: 1.5em;
        }

        ::v-deep(.user-stats) {
          margin-top: $default-margin * 0.5;
          align-content: space-between;
          flex-wrap: wrap;
          gap: $default-padding;

          .user-stat {
            padding: 0;
            flex-direction: row;
            .distance,
            .stat-number {
              font-size: 1.2em;
            }
          }
        }
      }
    }

    @media screen and (max-width: $x-small-limit) {
      ::v-deep(.user-picture) {
        img {
          height: 50px;
          width: 50px;
        }
        .no-picture {
          font-size: 3em;
        }
      }
      .user-details {
        .user-name {
          font-size: 1.5em;
        }

        ::v-deep(.user-stats) {
          gap: $default-padding * 0.5;

          .user-stat {
            .distance,
            .stat-number {
              font-size: 1em;
            }
          }
        }
      }
    }
  }
</style>
