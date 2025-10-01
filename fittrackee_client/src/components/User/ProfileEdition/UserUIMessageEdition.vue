<template>
  <div id="user-messages-edition">
    <h1>
      {{ $t('user.PROFILE.MESSAGES_PREFERENCES') }}
    </h1>
    <div class="notifications-form form-box">
      <ErrorMessage :message="errorMessages" v-if="errorMessages" />
      <form @submit.prevent="updatePreferences">
        <div class="form-items form-checkboxes">
          <span class="checkboxes-label">
            {{
              capitalize(
                $t(
                  `user.PROFILE.MESSAGES.warning_about_large_number_of_workouts_on_map`
                )
              )
            }}:
          </span>
          <div class="checkboxes">
            <label>
              <input
                type="radio"
                name="warning_about_large_number_of_workouts_on_map_true"
                :checked="warningOnLargeNumberOfWorkouts"
                :disabled="authUserLoading"
                @input="warningOnLargeNumberOfWorkouts = true"
              />
              <span class="checkbox-label">{{ $t('common.ENABLED') }}</span>
            </label>
            <label>
              <input
                type="radio"
                name="warning_about_large_number_of_workouts_on_map_false"
                :checked="!warningOnLargeNumberOfWorkouts"
                :disabled="authUserLoading"
                @input="warningOnLargeNumberOfWorkouts = false"
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
            @click.prevent="$router.push('/profile/messages')"
          >
            {{ $t('buttons.CANCEL') }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
  import { capitalize, ref, onMounted, toRefs } from 'vue'
  import type { Ref } from 'vue'

  import useApp from '@/composables/useApp'
  import useAuthUser from '@/composables/useAuthUser'
  import { AUTH_USER_STORE } from '@/store/constants.ts'
  import type { IAuthUserProfile } from '@/types/user'
  import { useStore } from '@/use/useStore'

  interface Props {
    user: IAuthUserProfile
  }
  const props = defineProps<Props>()
  const { user } = toRefs(props)

  const store = useStore()

  const { errorMessages } = useApp()
  const { authUserLoading } = useAuthUser()

  const warningOnLargeNumberOfWorkouts: Ref<boolean> = ref(true)

  function updatePreferences() {
    store.dispatch(AUTH_USER_STORE.ACTIONS.UPDATE_USER_MESSAGE_PREFERENCES, {
      preferences: {
        warning_about_large_number_of_workouts_on_map:
          warningOnLargeNumberOfWorkouts.value,
      },
      redirectToProfile: true,
    })
  }

  onMounted(() => {
    if (user.value) {
      warningOnLargeNumberOfWorkouts.value =
        user.value.messages_preferences
          .warning_about_large_number_of_workouts_on_map !== false
    }
  })
</script>

<style lang="scss" scoped>
  @use '~@/scss/vars.scss' as *;
  #user-messages-edition {
    padding-top: $default-padding;

    h1 {
      font-size: 1.05em;
      font-weight: bold;
    }

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
