<template>
  <div class="box">
    <div class="user-card">
      <div class="user-header">
        <UserPicture :user="user" />
        <router-link
          class="user-name"
          :to="`/users/${
            user.is_remote ? user.fullname : user.username
          }?from=users`"
        >
          {{ user.username }}
        </router-link>
        <div class="remote-user-account" v-if="user.is_remote">
          {{ user.fullname }}
        </div>
      </div>
      <UserStats :user="user" />
    </div>
    <UserRelationshipActions
      :authUser="authUser"
      :user="user"
      :from="from ? from : 'userCard'"
      :displayFollowsYou="true"
      @updatedUser="emitUser"
    />
    <ErrorMessage
      :message="errorMessages"
      v-if="errorMessages && updatedUser === user.username"
    />
  </div>
</template>

<script setup lang="ts">
  import { ComputedRef, computed, toRefs } from 'vue'

  import UserPicture from '@/components/User/UserPicture.vue'
  import UserRelationshipActions from '@/components/User/UserRelationshipActions.vue'
  import UserStats from '@/components/User/UserStats.vue'
  import { ROOT_STORE } from '@/store/constants'
  import { IAuthUserProfile, IUserProfile } from '@/types/user'
  import { useStore } from '@/use/useStore'

  interface Props {
    authUser: IAuthUserProfile
    user: IUserProfile
    updatedUser?: string
    from?: string
  }
  const props = defineProps<Props>()

  const store = useStore()

  const { from } = toRefs(props)

  const { authUser, updatedUser, user } = toRefs(props)
  const errorMessages: ComputedRef<string | string[] | null> = computed(
    () => store.getters[ROOT_STORE.GETTERS.ERROR_MESSAGES]
  )
  const emit = defineEmits(['updatedUserRelationship'])

  function emitUser(username: string) {
    emit('updatedUserRelationship', username)
  }
</script>

<style lang="scss" scoped>
  @import '~@/scss/vars.scss';

  .box {
    padding: $default-padding $default-padding * 2;
    .user-card {
      display: flex;
      min-height: 140px;

      .user-header {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: $default-margin;
        margin: $default-margin 0;
        width: 50%;

        ::v-deep(.user-picture) {
          img {
            height: 70px;
            width: 70px;
          }
          .no-picture {
            font-size: 4.4em;
          }
        }

        .remote-user-account {
          font-size: 0.8em;
          font-style: italic;
          margin-top: -10px;
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
