<template>
  <div class="user-actions" v-if="!isAuthUser(user, authUser)">
    <div v-if="user.is_followed_by !== 'pending'">
      <button
        @click="
          updateRelationship(getUserName(user), user.is_followed_by === 'true')
        "
        :class="{ danger: user.is_followed_by === 'true' }"
      >
        {{
          capitalize(
            $t(
              `user.RELATIONSHIPS.${
                user.is_followed_by === 'true' ? 'UN' : ''
              }FOLLOW`
            )
          )
        }}
      </button>
    </div>
    <div v-else>
      <button @click="updateRelationship(getUserName(user), true)">
        {{ capitalize($t('user.RELATIONSHIPS.CANCEL_FOLLOW_REQUEST')) }}
      </button>
    </div>
    <div
      class="follows-you"
      v-if="displayFollowsYou && user.follows === 'true'"
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
  import { capitalize, toRefs, withDefaults } from 'vue'

  import { USERS_STORE } from '@/store/constants'
  import { IAuthUserProfile, IUserProfile } from '@/types/user'
  import { useStore } from '@/use/useStore'
  import { isAuthUser, getUserName } from '@/utils/user'

  interface Props {
    authUser: IAuthUserProfile
    user: IUserProfile
    from: string
    displayFollowsYou?: boolean
  }
  const props = withDefaults(defineProps<Props>(), {
    displayFollowsYou: false,
  })

  const store = useStore()

  const { authUser, from, user, displayFollowsYou } = toRefs(props)

  const emit = defineEmits(['updatedUser'])

  function updateRelationship(username: string, following: boolean) {
    emit('updatedUser', username)
    store.dispatch(USERS_STORE.ACTIONS.UPDATE_RELATIONSHIP, {
      username,
      action: `${following ? 'un' : ''}follow`,
      from: from.value,
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

    .pending {
      border-radius: $border-radius;
      padding: $default-padding * 0.5 $default-padding;
      background-color: var(--text-background-color);
    }
  }
</style>
