<template>
  <div id="user-notifications-edition">
    <div class="notifications-form form-box">
      <ErrorMessage :message="errorMessages" v-if="errorMessages" />
      <form @submit.prevent="updatePreferences">
        <div
          class="form-items form-checkboxes"
          v-for="type in notificationTypes"
          :key="type"
        >
          <span class="checkboxes-label">
            {{ capitalize($t(`user.PROFILE.NOTIFICATIONS.${type}`)) }}:
          </span>
          <div class="checkboxes">
            <label>
              <input
                type="radio"
                :id="type"
                :name="type"
                :checked="notificationsForm[type]"
                :disabled="authUserLoading"
                @input="updateValue(type, true)"
              />
              <span class="checkbox-label">{{ $t('common.ENABLED') }}</span>
            </label>
            <label>
              <input
                type="radio"
                :id="type"
                :name="type"
                :checked="!notificationsForm[type]"
                :disabled="authUserLoading"
                @input="updateValue(type, false)"
              />
              <span class="checkbox-label">{{ $t('common.DISABLED') }}</span>
            </label>
          </div>
        </div>
        <div class="form-buttons">
          <button class="confirm" type="submit">
            {{ $t('buttons.SUBMIT') }}
          </button>
          <button
            class="cancel"
            @click.prevent="$router.push('/profile/notifications')"
          >
            {{ $t('buttons.CANCEL') }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
  import { capitalize, computed, reactive, onMounted, toRefs } from 'vue'
  import type { ComputedRef, Reactive } from 'vue'

  import useApp from '@/composables/useApp'
  import useAuthUser from '@/composables/useAuthUser'
  import { AUTH_USER_STORE } from '@/store/constants.ts'
  import type {
    TNotificationPreferences,
    TNotificationTypeWithPreferences,
  } from '@/types/notifications.ts'
  import type { IAuthUserProfile } from '@/types/user'
  import { useStore } from '@/use/useStore'
  import { getNotificationTypes } from '@/utils/notifications.ts'

  interface Props {
    user: IAuthUserProfile
  }
  const props = defineProps<Props>()
  const { user } = toRefs(props)

  const store = useStore()

  const { errorMessages } = useApp()
  const { authUserLoading } = useAuthUser()
  const notificationTypes: ComputedRef<TNotificationTypeWithPreferences[]> =
    computed(() => getNotificationTypes(user.value.role))

  const notificationsForm: Reactive<TNotificationPreferences> = reactive({
    account_creation: true,
    comment_like: true,
    comment_reply: true,
    follow: true,
    follow_request: true,
    follow_request_approved: true,
    mention: true,
    workout_comment: true,
    workout_like: true,
  })

  function updateUserForm(notificationPreferences: TNotificationPreferences) {
    notificationTypes.value.forEach((type) => {
      notificationsForm[type] =
        type in notificationPreferences ? notificationPreferences[type] : true
    })
  }
  function updateValue(key: TNotificationTypeWithPreferences, value: boolean) {
    notificationsForm[key] = value
  }
  function updatePreferences() {
    store.dispatch(
      AUTH_USER_STORE.ACTIONS.UPDATE_USER_NOTIFICATIONS_PREFERENCES,
      notificationsForm
    )
  }

  onMounted(() => {
    if (user.value) {
      updateUserForm(user.value.notification_preferences)
    }
  })
</script>

<style lang="scss" scoped>
  @use '~@/scss/vars.scss' as *;
  #user-notifications-edition {
    padding-top: $default-padding;
    .form-items {
      padding-top: $default-padding * 0.5;
    }

    .form-checkboxes {
      .checkboxes-label {
        font-weight: bold;
      }
      .checkboxes {
        display: flex;
        flex-wrap: wrap;
        label {
          font-weight: normal;
        }
      }
    }

    .form-buttons {
      display: flex;
      gap: $default-padding;
      margin: $default-margin 0;
    }
  }
</style>
