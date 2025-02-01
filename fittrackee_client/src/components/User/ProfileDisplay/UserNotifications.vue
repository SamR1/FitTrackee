<template>
  <h1>
    {{ $t('user.PROFILE.NOTIFICATION_PREFERENCES') }}
  </h1>
  <div id="user-notifications" class="description-list">
    <dl>
      <template v-for="type in notificationTypes" :key="type">
        <dt>{{ capitalize($t(`user.PROFILE.NOTIFICATIONS.${type}`)) }}:</dt>
        <dd>
          <i
            :class="`fa fa-${isNotificationEnabled(type) ? 'check' : 'times'} fa-padding`"
            aria-hidden="true"
          />
          {{ $t(`common.${isNotificationEnabled(type) ? 'EN' : 'DIS'}ABLED`) }}
        </dd>
      </template>
    </dl>
    <div class="profile-buttons">
      <button @click="$router.push('/profile/edit/notifications')">
        {{ $t('user.PROFILE.EDIT_NOTIFICATION_PREFERENCES') }}
      </button>
      <button @click="$router.push('/notifications')">
        {{ capitalize($t('notifications.NOTIFICATIONS', 0)) }}
      </button>
      <button @click="$router.push('/')">{{ $t('common.HOME') }}</button>
    </div>
  </div>
</template>

<script setup lang="ts">
  import { capitalize, computed, toRefs } from 'vue'
  import type { ComputedRef } from 'vue'

  import type { TNotificationTypeWithPreferences } from '@/types/notifications.ts'
  import type { IAuthUserProfile } from '@/types/user'
  import { getNotificationTypes } from '@/utils/notifications.ts'

  interface Props {
    user: IAuthUserProfile
  }
  const props = defineProps<Props>()
  const { user } = toRefs(props)

  const notificationTypes: ComputedRef<TNotificationTypeWithPreferences[]> =
    computed(() => getNotificationTypes(user.value.role))

  function isNotificationEnabled(type: TNotificationTypeWithPreferences) {
    if (!(type in user.value.notification_preferences)) {
      return true
    }
    return user.value.notification_preferences[type]
  }
</script>

<style lang="scss" scoped>
  @use '~@/scss/vars.scss' as *;
  h1 {
    font-size: 1.05em;
    font-weight: bold;
  }
  .profile-buttons {
    flex-wrap: wrap;
  }
</style>
