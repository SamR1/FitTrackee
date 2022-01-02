<template>
  <div class="box user-header">
    <UserPicture :user="user" />
    <div class="user-details">
      <div class="user-name">{{ user.username }}</div>
      <UserStats :authUser="authUser" :user="user" />
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

  const { authUser, user } = toRefs(props)
</script>

<style lang="scss" scoped>
  @import '~@/scss/vars.scss';

  .user-header {
    display: flex;
    align-items: stretch;

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
        gap: $default-padding * 4;
        .user-stat {
          flex-direction: column;
          align-items: center;
          padding-top: $default-padding;

          ::v-deep(.distance),
          .stat-number {
            font-size: 1.5em;
          }
        }
      }

      @media screen and (max-width: $x-small-limit) {
        .user-name {
          font-size: 1.5em;
        }

        ::v-deep(.user-stats) {
          gap: $default-padding * 2;
          .user-stat {
            ::v-deep(.distance),
            .stat-number {
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
