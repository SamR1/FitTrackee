<template>
  <div class="box">
    <div class="user-header">
      <div class="follows-you" v-if="user.follows === 'true'">
        {{ $t('user.RELATIONSHIPS.FOLLOWS_YOU') }}
      </div>
      <UserPicture :user="user" />
      <div class="user-details">
        <div class="user-name">{{ user.username }}</div>
        <UserStats :user="user" />
      </div>
    </div>
    <AlertMessage
      message="user.ACCOUNT_SUSPENDED_AT"
      :param="suspensionDate"
      v-if="user.suspended_at !== null"
    >
      <template #additionalMessage v-if="displayMakeAppeal">
        <router-link to="/profile/suspension" class="appeal-link">
          {{ $t('user.APPEAL') }}
        </router-link>
      </template>
    </AlertMessage>
  </div>
</template>

<script setup lang="ts">
  import { computed, type ComputedRef, toRefs } from 'vue'
  import { useRoute } from 'vue-router'

  import UserPicture from '@/components/User/UserPicture.vue'
  import UserStats from '@/components/User/UserStats.vue'
  import { AUTH_USER_STORE, ROOT_STORE } from '@/store/constants'
  import type { IDisplayOptions } from '@/types/application'
  import type { IAuthUserProfile, IUserProfile } from '@/types/user'
  import { useStore } from '@/use/useStore'
  import { formatDate } from '@/utils/dates'

  interface Props {
    user: IUserProfile
  }
  const props = defineProps<Props>()

  const { user } = toRefs(props)

  const store = useStore()
  const route = useRoute()

  const authUser: ComputedRef<IAuthUserProfile> = computed(
    () => store.getters[AUTH_USER_STORE.GETTERS.AUTH_USER_PROFILE]
  )
  const displayOptions: ComputedRef<IDisplayOptions> = computed(
    () => store.getters[ROOT_STORE.GETTERS.DISPLAY_OPTIONS]
  )
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
