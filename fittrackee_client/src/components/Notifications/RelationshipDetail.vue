<template>
  <div class="follow-request">
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
      </button>
      <button
        @click="updateFollowRequest(notification.from.username, 'reject')"
        class="danger"
      >
        <i class="fa fa-times" aria-hidden="true" />
      </button>
    </div>
  </div>
</template>
<script lang="ts" setup>
  import { toRefs } from 'vue'

  import UserPicture from '@/components/User/UserPicture.vue'
  import { AUTH_USER_STORE } from '@/store/constants'
  import { INotification } from '@/types/notifications'
  import { TFollowRequestAction } from '@/types/user'
  import { useStore } from '@/use/useStore'

  interface Props {
    notification: INotification
  }

  const props = defineProps<Props>()
  const { notification } = toRefs(props)

  const store = useStore()

  const emit = defineEmits(['updatedUserRelationship'])

  function updateFollowRequest(username: string, action: TFollowRequestAction) {
    store
      .dispatch(AUTH_USER_STORE.ACTIONS.UPDATE_FOLLOW_REQUESTS, {
        username,
        action,
      })
      .then(() => emit('updatedUserRelationship'))
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
        width: 60px;
      }
    }
  }
</style>
