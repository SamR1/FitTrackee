<template>
  <div class="box">
    <div class="user-card">
      <div class="user-header">
        <UserPicture :user="user" />
        <router-link
          class="user-name"
          :to="
            $route.path.startsWith('/admin')
              ? `/admin/users/${user.username}`
              : `/users/${user.username}?from=users`
          "
          :title="user.username"
        >
          {{ user.username }}
        </router-link>
      </div>
      <div class="stats-role">
        <UserStats :user="user" />
        <div class="role" v-if="role">
          <div class="user-role">
            {{ $t(role) }}
          </div>
        </div>
      </div>
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
      v-if="'is_active' in user && !user.is_active"
    />
    <AlertMessage
      message="user.ACCOUNT_SUSPENDED_AT"
      :param="suspensionDate"
      v-if="'suspended_at' in user && user.suspended_at !== null"
    >
      <template #additionalMessage v-if="displayReportLink">
        <i18n-t keypath="common.SEE_REPORT" tag="span">
          <router-link :to="`/admin/reports/${user.suspension_report_id}`">
            #{{ user.suspension_report_id }}
          </router-link>
        </i18n-t>
      </template>
    </AlertMessage>
    <ErrorMessage
      :message="errorMessages"
      v-if="errorMessages && updatedUser && updatedUser === user.username"
    />
  </div>
</template>

<script setup lang="ts">
  import { computed, toRefs } from 'vue'
  import type { ComputedRef } from 'vue'
  import { useRoute } from 'vue-router'

  import UserPicture from '@/components/User/UserPicture.vue'
  import UserRelationshipActions from '@/components/User/UserRelationshipActions.vue'
  import UserStats from '@/components/User/UserStats.vue'
  import useApp from '@/composables/useApp'
  import useAuthUser from '@/composables/useAuthUser'
  import type { IAuthUserProfile, IUserLightProfile } from '@/types/user'
  import { formatDate } from '@/utils/dates'

  interface Props {
    authUser: IAuthUserProfile
    user: IUserLightProfile
    updatedUser?: string | null
    from?: string | null
    hideRelationship?: boolean
  }
  const props = withDefaults(defineProps<Props>(), {
    from: null,
    hideRelationship: false,
  })
  const { authUser, from, hideRelationship, updatedUser, user } = toRefs(props)

  const route = useRoute()

  const { authUserHasModeratorRights } = useAuthUser()
  const { errorMessages } = useApp()

  const emit = defineEmits(['updatedUserRelationship'])

  const suspensionDate: ComputedRef<string | null> = computed(() =>
    user.value.suspended_at
      ? formatDate(
          user.value.suspended_at,
          authUser.value.timezone,
          authUser.value.date_format
        )
      : null
  )
  const displayReportLink: ComputedRef<boolean> = computed(
    () =>
      authUserHasModeratorRights.value &&
      route.params.reportId != user.value.suspension_report_id?.toString()
  )
  const role: ComputedRef<string> = computed(() =>
    user.value.role !== 'user' ? `user.ROLES.${user.value.role}` : ''
  )

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
      }
      .stats-role {
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        width: 50%;
        .role {
          display: flex;
          justify-content: flex-end;
          margin-bottom: $default-margin * 0.5;
        }

        ::v-deep(.user-stats) {
          flex-direction: column;
          align-items: flex-end;
          margin: $default-margin 0;
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
  }
</style>
