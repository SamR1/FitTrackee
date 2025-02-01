<template>
  <div class="user-actions" v-if="!isAuthUser(user, authUser)">
    <div v-if="user.blocked" class="blocked-user">
      <div class="blocked">
        {{ $t('user.RELATIONSHIPS.BLOCKED') }}
      </div>
      <button @click="updateBlock(user.username, false)">
        {{ $t('buttons.UNBLOCK') }}
      </button>
    </div>
    <div v-else-if="user.is_followed_by !== 'pending'" class="actions-buttons">
      <button
        @click="
          updateRelationship(getUserName(user), user.is_followed_by === 'true')
        "
        :class="{ danger: user.is_followed_by === 'true' }"
      >
        {{ $t(`buttons.${user.is_followed_by === 'true' ? 'UN' : ''}FOLLOW`) }}
      </button>
      <button @click="updateBlock(user.username, true)">
        {{ $t('buttons.BLOCK') }}
      </button>
    </div>
    <div v-else>
      <button @click="updateRelationship(getUserName(user), true)">
        {{ $t('buttons.CANCEL_FOLLOW_REQUEST') }}
      </button>
    </div>
    <div
      class="follows-you"
      v-if="
        displayFollowsYou && user.follows === 'true' && from !== 'notifications'
      "
    >
      {{ $t('user.RELATIONSHIPS.FOLLOWS_YOU') }}
    </div>
  </div>
  <div
    class="user-actions"
    v-if="isAuthUser(user, authUser) && from !== 'userInfos'"
  >
    <div class="follows-you">
      {{ $t('user.YOU') }}
    </div>
  </div>
</template>

<script lang="ts" setup>
  import { toRefs } from 'vue'

  import { USERS_STORE } from '@/store/constants'
  import type { IAuthUserProfile, IUserLightProfile } from '@/types/user'
  import { useStore } from '@/use/useStore'
  import { isAuthUser, getUserName } from '@/utils/user'

  interface Props {
    authUser: IAuthUserProfile
    user: IUserLightProfile
    from: string
    displayFollowsYou?: boolean
  }
  const props = withDefaults(defineProps<Props>(), {
    displayFollowsYou: false,
  })
  const { authUser, from, user, displayFollowsYou } = toRefs(props)

  const emit = defineEmits(['updatedUser'])

  const store = useStore()

  function updateRelationship(username: string, following: boolean) {
    emit('updatedUser', username)
    store.dispatch(USERS_STORE.ACTIONS.UPDATE_RELATIONSHIP, {
      username,
      action: `${following ? 'un' : ''}follow`,
      from: from.value,
    })
  }
  function updateBlock(username: string, block: boolean) {
    emit('updatedUser', username)
    store.dispatch(USERS_STORE.ACTIONS.UPDATE_RELATIONSHIP, {
      username,
      action: `${block ? '' : 'un'}block`,
      from: from.value,
    })
  }
</script>

<style lang="scss" scoped>
  @use '~@/scss/vars.scss' as *;

  .user-actions {
    display: flex;
    justify-content: space-between;
    align-items: flex-end;
    min-height: 35px;
    gap: $default-padding * 0.5;

    .pending {
      border-radius: $border-radius;
      padding: $default-padding * 0.5 $default-padding;
      background-color: var(--text-background-color);
    }
    .actions-buttons,
    .blocked-user {
      display: flex;
      gap: $default-padding * 0.5;
      align-items: center;
      button {
        text-transform: capitalize;
        white-space: nowrap;
      }
    }
    .follows-you {
      white-space: nowrap;
    }
  }
</style>
