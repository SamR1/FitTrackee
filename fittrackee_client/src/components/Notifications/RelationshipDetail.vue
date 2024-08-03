<template>
  <div class="follow-request" v-if="notification.from">
    <div class="follow-request-user">
      <UserPicture :user="notification.from" />
      <div class="user-name">
        <router-link :to="`/users/${notification.from.username}`">
          {{ notification.from.username }}
        </router-link>
      </div>
    </div>
    <div
      class="follow-request-actions"
      v-if="notification.type === 'follow_request'"
    >
      <button
        @click="updateFollowRequest(notification.from.username, 'accept')"
      >
        <i class="fa fa-check" aria-hidden="true" />
        {{ $t('buttons.ACCEPT') }}
      </button>
      <button
        @click="updateFollowRequest(notification.from.username, 'reject')"
        class="danger"
      >
        <i class="fa fa-times" aria-hidden="true" />
        {{ $t('buttons.REJECT') }}
      </button>
    </div>
    <div class="follow-request-actions" v-else>
      <UserRelationshipActions
        :authUser="authUser"
        :user="notification.from"
        from="notifications"
        :displayFollowsYou="true"
        @updatedUser="() => emit('updatedUserRelationship')"
      />
    </div>
  </div>
</template>
<script lang="ts" setup>
  import { toRefs } from 'vue'

  import UserPicture from '@/components/User/UserPicture.vue'
  import UserRelationshipActions from '@/components/User/UserRelationshipActions.vue'
  import { AUTH_USER_STORE } from '@/store/constants'
  import type { INotification } from '@/types/notifications'
  import type { IAuthUserProfile, TFollowRequestAction } from '@/types/user'
  import { useStore } from '@/use/useStore'

  interface Props {
    authUser: IAuthUserProfile
    notification: INotification
  }
  const props = defineProps<Props>()
  const { authUser, notification } = toRefs(props)

  const emit = defineEmits(['updatedUserRelationship'])

  const store = useStore()

  function updateFollowRequest(username: string, action: TFollowRequestAction) {
    store.dispatch(AUTH_USER_STORE.ACTIONS.UPDATE_FOLLOW_REQUESTS, {
      username,
      action,
    })
    emit('updatedUserRelationship')
  }
</script>

<style scoped lang="scss">
  @import '~@/scss/vars';

  .follow-request {
    display: flex;
    flex-direction: row;
    align-items: center;
    justify-content: space-between;
    .follow-request-user {
      display: flex;
      align-items: center;
      .user-picture {
        min-width: initial;
        padding: 0 $default-padding;
        img {
          height: 60px;
          width: 60px;
        }
        .no-picture {
          font-size: 3.8em;
        }
      }
    }
    .follow-request-actions {
      display: flex;
      flex-direction: column;
      gap: $default-padding;

      button {
        display: flex;
        gap: $default-padding;
        .fa {
          line-height: 20px;
        }
      }
    }
  }
</style>
