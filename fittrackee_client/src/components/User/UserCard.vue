<template>
  <div class="box">
    <div class="user-card">
      <div class="user-header">
        <UserPicture :user="user" />
        <router-link
          class="user-name"
          :to="`/users/${user.username}?from=admin`"
        >
          {{ user.username }}
        </router-link>
      </div>
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
    authUser: IAuthUserProfile
    user: IUserProfile
  }
  const props = defineProps<Props>()

  const { authUser, user } = toRefs(props)
</script>

<style lang="scss" scoped>
  @import '~@/scss/vars.scss';

  .box {
    padding: $default-padding $default-padding * 2;
    .user-card {
      display: flex;

      .user-header {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: $default-margin;
        margin: $default-margin 0;
        width: 50%;

        .user-name {
          //font-size: 0.8em;
        }
        ::v-deep(.user-picture) {
          img {
            height: 70px;
            width: 70px;
          }
          .no-picture {
            font-size: 4.4em;
          }
        }
      }
      ::v-deep(.user-stats) {
        flex-direction: column;
        align-items: flex-end;
        margin: $default-margin 0;
        width: 50%;
        .distance {
          padding-right: $default-padding * 0.1;
        }
        .stat-number {
          padding-right: 0;
        }
        .distance,
        .stat-number,
        .stat-label {
          font-size: 0.95em;
        }
      }
    }
  }
</style>
