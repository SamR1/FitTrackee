<template>
  <div class="box workout-user">
    <div class="user-img-name">
      <UserPicture :user="user" />
      <router-link
        class="user-name"
        :to="`/users/${getUserName(user)}?from=users`"
      >
        {{ user.username }}
        <div v-if="user.is_remote" class="user-remote-fullname">
          {{ user.fullname }}
        </div>
      </router-link>
    </div>
    <UserStats :user="user" />
  </div>
</template>

<script setup lang="ts">
  import { toRefs } from 'vue'

  import UserPicture from '@/components/User/UserPicture.vue'
  import UserStats from '@/components/User/UserStats.vue'
  import type { IUserProfile } from '@/types/user'
  import { getUserName } from '@/utils/user'

  interface Props {
    user: IUserProfile
  }
  const props = defineProps<Props>()
  const { user } = toRefs(props)
</script>

<style scoped lang="scss">
  @use '~@/scss/vars.scss' as *;

  .workout-user {
    display: flex;
    flex-direction: row;
    gap: $default-padding * 2;
    align-items: center;

    .user-img-name {
      display: flex;
      align-items: center;
      gap: $default-padding;

      ::v-deep(.user-picture) {
        padding-left: $default-padding;
        min-width: 0;
        img {
          height: 48px;
          width: 48px;
        }
        .no-picture {
          font-size: 3em;
        }
      }

      .user-name {
        font-size: 1.3em;
        .user-remote-fullname {
          font-size: 0.65em;
          font-style: italic;
        }
      }
    }

    @media screen and (max-width: $small-limit) {
      flex-direction: column;
      align-items: flex-start;
      gap: 0;
    }

    @media screen and (max-width: $x-small-limit) {
      .user-img-name {
        ::v-deep(.user-picture) {
          padding-left: $default-padding;
          min-width: 0;
          img {
            height: 30px;
            width: 30px;
          }
          .no-picture {
            font-size: 2em;
          }
        }

        .user-name {
          font-size: 1em;
          padding-left: $default-padding * 0.5;
          .user-remote-fullname {
            font-size: 0.8em;
          }
        }
      }
      ::v-deep(.user-stats) {
        flex-wrap: wrap;
      }
    }
  }
</style>
