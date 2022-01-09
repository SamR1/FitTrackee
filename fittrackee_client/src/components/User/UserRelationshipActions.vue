<template>
  <div class="user-actions" v-if="user.username !== authUser.username">
    <div v-if="user.is_followed_by !== 'pending'">
      <button
        @click="
          updateRelationship(user.username, user.is_followed_by === 'true')
        "
        :class="{ danger: user.is_followed_by === 'true' }"
      >
        {{
          capitalize(
            $t(`user.${user.is_followed_by === 'true' ? 'UN' : ''}FOLLOW`)
          )
        }}
      </button>
    </div>
    <div v-else>
      <button @click="updateRelationship(user.username, true)">
        {{ capitalize($t('user.CANCEL_FOLLOW_REQUEST')) }}
      </button>
    </div>
    <div class="follows-you" v-if="user.follows === 'true'">
      {{ $t('user.FOLLOWS_YOU') }}
    </div>
  </div>
  <div
    class="user-actions"
    v-if="user.username === authUser.username && !fromUserInfos"
  >
    <div class="follows-you">
      {{ $t('user.YOU') }}
    </div>
  </div>
</template>

<script lang="ts" setup>
  import { capitalize, toRefs } from 'vue'

  import { USERS_STORE } from '@/store/constants'
  import { IAuthUserProfile, IUserProfile } from '@/types/user'
  import { useStore } from '@/use/useStore'

  interface Props {
    authUser: IAuthUserProfile
    user: IUserProfile
    fromUserInfos: boolean
  }
  const props = defineProps<Props>()

  const store = useStore()

  const { authUser, fromUserInfos, user } = toRefs(props)

  const emit = defineEmits(['updatedUser'])

  function updateRelationship(username: string, following: boolean) {
    emit('updatedUser', username)
    store.dispatch(USERS_STORE.ACTIONS.UPDATE_RELATIONSHIP, {
      username,
      action: `${following ? 'un' : ''}follow`,
      fromUserInfos: fromUserInfos.value,
    })
  }
</script>

<style lang="scss" scoped>
  @import '~@/scss/vars.scss';

  .user-actions {
    display: flex;
    justify-content: space-between;
    align-items: flex-end;
    min-height: 35px;

    .follows-you {
      font-size: 0.7em;
      font-style: italic;
      text-transform: uppercase;
      padding: $default-padding * 0.5 $default-padding;
      background-color: var(--text-background-color);
      border-radius: $border-radius;
    }

    .pending {
      border-radius: $border-radius;
      padding: $default-padding * 0.5 $default-padding;
      background-color: var(--text-background-color);
    }
  }
</style>
