<template>
  <div class="box">
    <div class="user-header">
      <div class="follows-you" v-if="user.follows === 'true'">
        {{ $t('user.RELATIONSHIPS.FOLLOWS_YOU') }}
      </div>
      <div class="follows-you" v-else-if="user.username === authUser.username">
        {{ $t('user.YOU') }}
      </div>
      <UserPicture :user="user" />
      <div class="user-details">
        <div class="user-name">{{ user.username }}</div>
        <UserStats :user="user" />
      </div>
      <div class="user-role" v-if="role">
        {{ $t(role) }}
      </div>
    </div>
    <AlertMessage
      message="user.ACCOUNT_SUSPENDED_AT"
      :param="suspensionDate"
      v-if="'suspended_at' in user && user.suspended_at !== null"
    >
      <template
        #additionalMessage
        v-if="displayMakeAppeal || displayReportLink"
      >
        <router-link
          to="/profile/suspension"
          class="appeal-link"
          v-if="displayMakeAppeal"
        >
          {{ $t('user.APPEAL') }}
        </router-link>
        <i18n-t keypath="common.SEE_REPORT" v-if="displayReportLink">
          <router-link :to="`/admin/reports/${user.suspension_report_id}`">
            {{ user.suspension_report_id }}
          </router-link>
        </i18n-t>
      </template>
    </AlertMessage>
  </div>
</template>

<script setup lang="ts">
  import { computed, type ComputedRef, toRefs } from 'vue'
  import { useRoute } from 'vue-router'

  import UserPicture from '@/components/User/UserPicture.vue'
  import UserStats from '@/components/User/UserStats.vue'
  import useApp from '@/composables/useApp'
  import useAuthUser from '@/composables/useAuthUser'
  import type { IUserProfile } from '@/types/user'
  import { formatDate } from '@/utils/dates'

  interface Props {
    user: IUserProfile
  }
  const props = defineProps<Props>()
  const { user } = toRefs(props)

  const route = useRoute()

  const { displayOptions } = useApp()
  const { authUser, authUserHasModeratorRights } = useAuthUser()

  const suspensionDate: ComputedRef<string | null> = computed(() =>
    user.value.suspended_at
      ? formatDate(
          user.value.suspended_at,
          displayOptions.value.timezone,
          displayOptions.value.dateFormat
        )
      : ''
  )
  const displayMakeAppeal: ComputedRef<boolean> = computed(
    () =>
      user.value.suspended_at !== null &&
      route.name !== 'AuthUserAccountSuspension' &&
      user.value.username === authUser?.value.username
  )
  const displayReportLink: ComputedRef<boolean> = computed(
    () =>
      authUserHasModeratorRights.value &&
      user.value.suspension_report_id !== undefined
  )
  const role: ComputedRef<string> = computed(() =>
    user.value.role !== 'user' ? `user.ROLES.${user.value.role}` : ''
  )
</script>

<style lang="scss" scoped>
  @import '~@/scss/vars.scss';

  .user-header {
    display: flex;
    align-items: stretch;
    position: relative;

    .follows-you {
      position: absolute;
      margin-top: -$default-margin;
      margin-left: -$default-margin;
    }
    .user-role {
      position: absolute;
      bottom: 0;
      margin-bottom: -$default-margin;
      margin-left: -$default-margin;
    }

    ::v-deep(.user-picture) {
      min-width: 20%;
    }

    .user-details {
      flex-grow: 1;
      padding: $default-padding;
      display: flex;
      flex-direction: column;
      align-items: center;

      .user-name {
        font-size: 2em;
        height: 60%;
      }

      ::v-deep(.user-stats) {
        flex-wrap: nowrap;
        gap: $default-padding * 4;
        .user-stat {
          flex-direction: column;
          align-items: center;
          padding-top: $default-padding;

          .distance,
          .stat-number {
            font-size: 1.5em;
          }
        }
      }
    }

    @media screen and (max-width: $small-limit) {
      .user-details {
        .user-name {
          font-size: 1.5em;
        }

        ::v-deep(.user-stats) {
          margin-top: $default-margin * 0.5;
          align-content: space-between;
          flex-wrap: wrap;
          gap: $default-padding;

          .user-stat {
            padding: 0;
            flex-direction: row;
            .distance,
            .stat-number {
              font-size: 1.2em;
            }
          }
        }
      }
    }

    @media screen and (max-width: $x-small-limit) {
      ::v-deep(.user-picture) {
        img {
          height: 50px;
          width: 50px;
        }
        .no-picture {
          font-size: 3em;
        }
      }
      .user-details {
        .user-name {
          font-size: 1.5em;
        }

        ::v-deep(.user-stats) {
          flex-direction: column;
          gap: $default-padding * 0.5;

          .user-stat {
            .distance,
            .stat-number {
              font-size: 1em;
            }
          }
        }
      }
    }
  }
</style>
