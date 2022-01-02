<template>
  <div class="box">
    <div class="user-card">
      <div class="user-header">
        <UserPicture :user="user" />
        <router-link :to="`/users/${user.username}?from=admin`">
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

  .user-card {
    display: flex;

    .user-header {
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: $default-margin;
      margin: $default-margin;
      width: 50%;
      ::v-deep(.user-picture) {
        img {
          height: 60px;
          width: 60px;
        }
        .no-picture {
          font-size: 4em;
        }
      }
    }
    ::v-deep(.user-stats) {
      flex-direction: column;
      align-items: flex-end;
      margin: $default-margin;
      width: 50%;
    }
  }
</style>
