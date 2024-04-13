<template>
  <div class="box">
    <div class="user-card">
      <div class="user-header">
        <UserPicture :user="user" />
        <router-link
          class="user-name"
          :to="`/users/${getUserName(user)}?from=users`"
          :title="user.username"
        >
          {{ user.username }}
        </router-link>
        <div
          class="remote-user-account"
          v-if="user.is_remote"
          :title="user.fullname"
        >
          {{ user.fullname }}
        </div>
      </div>
      <UserStats :user="user" />
    </div>
    <UserRelationshipActions
      v-if="hideRelationship !== true"
      :authUser="authUser"
      :user="user"
      :from="from ? from : 'userCard'"
      :displayFollowsYou="true"
      @updatedUser="emitUser"
    />
    <AlertMessage
      message="user.THIS_USER_ACCOUNT_IS_INACTIVE"
      v-if="!user.is_active"
    />
    <AlertMessage
      message="user.ACCOUNT_SUSPENDED_AT"
      :param="suspensionDate"
      v-if="user.suspended_at !== null"
    />
    <ErrorMessage
      :message="errorMessages"
      v-if="
        errorMessages &&
        ((updatedUser && updatedUser === user.username) || !updatedUser)
      "
    />
  </div>
</template>

<script setup lang="ts">
  import { computed, toRefs } from 'vue'
  import type { ComputedRef } from 'vue'

  import UserPicture from '@/components/User/UserPicture.vue'
  import UserRelationshipActions from '@/components/User/UserRelationshipActions.vue'
  import UserStats from '@/components/User/UserStats.vue'
  import { ROOT_STORE } from '@/store/constants'
  import type { IEquipmentError } from '@/types/equipments'
  import type { IAuthUserProfile, IUserProfile } from '@/types/user'
  import { useStore } from '@/use/useStore'
  import { formatDate } from '@/utils/dates'
  import { getUserName } from '@/utils/user'

  interface Props {
    authUser: IAuthUserProfile
    user: IUserProfile
    updatedUser?: string | null
    from?: string
    hideRelationship?: boolean
  }
  const props = defineProps<Props>()

  const store = useStore()

  const { from } = toRefs(props)

  const { authUser, updatedUser, user, hideRelationship } = toRefs(props)
  const errorMessages: ComputedRef<string | string[] | IEquipmentError | null> =
    computed(() => store.getters[ROOT_STORE.GETTERS.ERROR_MESSAGES])
  const suspensionDate: ComputedRef<string | null> = computed(() =>
    user.value.suspended_at
      ? formatDate(
          user.value.suspended_at,
          authUser.value.timezone,
          authUser.value.date_format
        )
      : null
  )

  const emit = defineEmits(['updatedUserRelationship'])

  function emitUser(username: string) {
    emit('updatedUserRelationship', username)
  }
</script>

<style lang="scss" scoped>
  @import '~@/scss/vars.scss';

  .box {
    padding: $default-padding $default-padding * 1.2;
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

        .remote-user-account,
        .user-name {
          max-width: 170px;
          overflow: hidden;
          white-space: nowrap;
          text-overflow: ellipsis;
          @media screen and (max-width: $small-limit) {
            max-width: fit-content;
          }
          @media screen and (max-width: $x-small-limit) {
            max-width: 170px;
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
