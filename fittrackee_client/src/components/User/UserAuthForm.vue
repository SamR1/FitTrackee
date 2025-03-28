<template>
  <div
    id="user-auth-form"
    :class="`${
      ['reset', 'reset-request'].includes(action) ? action : 'user-form'
    }`"
  >
    <div id="user-form">
      <div
        class="form-box"
        :class="{
          disabled: registration_disabled,
        }"
      >
        <AlertMessage
          message="user.REGISTER_DISABLED"
          v-if="registration_disabled"
        />
        <AlertMessage
          message="admin.EMAIL_SENDING_DISABLED"
          v-if="sendingEmailDisabled"
        />
        <div
          class="info-box success-message"
          v-if="authUserSuccess || isRegistrationSuccess"
        >
          {{
            $t(
              `user.PROFILE.SUCCESSFUL_${
                isRegistrationSuccess
                  ? `REGISTRATION${
                      appConfig.is_email_sending_enabled ? '_WITH_EMAIL' : ''
                    }`
                  : 'UPDATE'
              }`
            )
          }}
        </div>
        <form
          :class="{ errors: formErrors }"
          @submit.prevent="onSubmit(action)"
        >
          <div class="form-items">
            <label for="username" v-if="action === 'register'">
              {{ $t('user.USERNAME', 0) }}
            </label>
            <input
              v-if="action === 'register'"
              id="username"
              :disabled="registration_disabled"
              required
              pattern="[a-zA-Z0-9_]+"
              minlength="3"
              maxlength="30"
              @invalid="invalidateForm"
              v-model="formData.username"
              autocomplete="username"
            />
            <div v-if="action === 'register'" class="form-info">
              <i class="fa fa-info-circle" aria-hidden="true" />
              {{ $t('user.USERNAME_INFO') }}
            </div>
            <label for="email" v-if="action !== 'reset'">
              {{ $t('user.EMAIL', 0) }}
            </label>
            <input
              v-if="action !== 'reset'"
              id="email"
              :disabled="registration_disabled || sendingEmailDisabled"
              required
              @invalid="invalidateForm"
              type="email"
              v-model="formData.email"
              autocomplete="email"
            />
            <div
              v-if="
                [
                  'reset-request',
                  'register',
                  'account-confirmation-resend',
                ].includes(action)
              "
              class="form-info"
            >
              <i class="fa fa-info-circle" aria-hidden="true" />
              {{ $t('user.EMAIL_INFO') }}
            </div>
            <label
              for="password"
              v-if="
                !['account-confirmation-resend', 'reset-request'].includes(
                  action
                )
              "
            >
              {{
                $t(`user.${action === 'reset' ? 'ENTER_PASSWORD' : 'PASSWORD'}`)
              }}
            </label>
            <PasswordInput
              v-if="
                !['account-confirmation-resend', 'reset-request'].includes(
                  action
                )
              "
              id="password"
              :disabled="registration_disabled"
              :required="true"
              :password="formData.password"
              :checkStrength="['reset', 'register'].includes(action)"
              @updatePassword="updatePassword"
              @passwordError="invalidateForm"
              autocomplete="current-password"
            />
            <label
              v-if="action === 'register'"
              for="accepted_policy"
              class="accepted_policy"
            >
              <input
                type="checkbox"
                id="accepted_policy"
                :disabled="registration_disabled"
                required
                @invalid="invalidateForm"
                v-model="formData.accepted_policy"
              />
              <span>
                <i18n-t keypath="user.READ_AND_ACCEPT_PRIVACY_POLICY">
                  <router-link to="/privacy-policy" target="_blank">
                    {{ $t('privacy_policy.TITLE') }}
                  </router-link>
                </i18n-t>
              </span>
            </label>
          </div>
          <button
            type="submit"
            :disabled="registration_disabled || sendingEmailDisabled"
          >
            {{ $t(buttonText) }}
          </button>
        </form>
        <div v-if="action === 'login'">
          <router-link class="links" to="/register">
            {{ $t('user.REGISTER') }}
          </router-link>
          <span v-if="appConfig.is_email_sending_enabled">-</span>
          <router-link
            v-if="appConfig.is_email_sending_enabled"
            class="links"
            to="/password-reset/request"
          >
            {{ $t('user.PASSWORD_FORGOTTEN') }}
          </router-link>
        </div>
        <div v-if="action === 'register'">
          <span class="account">{{ $t('user.ALREADY_HAVE_ACCOUNT') }}</span>
          <router-link class="links" to="/login">
            {{ $t('user.LOGIN') }}
          </router-link>
        </div>
        <div
          v-if="
            ['login', 'register'].includes(action) &&
            appConfig.is_email_sending_enabled
          "
        >
          <router-link class="links" to="/account-confirmation/resend">
            {{ $t('user.ACCOUNT_CONFIRMATION_NOT_RECEIVED') }}
          </router-link>
        </div>
        <ErrorMessage :message="errorMessages" v-if="errorMessages" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
  import { computed, reactive, ref, toRefs, watch } from 'vue'
  import type { Reactive, ComputedRef, Ref } from 'vue'
  import { useRoute } from 'vue-router'

  import PasswordInput from '@/components/Common/PasswordInput.vue'
  import useApp from '@/composables/useApp'
  import useAuthUser from '@/composables/useAuthUser'
  import { AUTH_USER_STORE, ROOT_STORE } from '@/store/constants'
  import type { ILoginRegisterFormData, TToken } from '@/types/user'
  import { useStore } from '@/use/useStore'

  interface Props {
    action: string
    token?: TToken
  }
  const props = withDefaults(defineProps<Props>(), {
    token: '',
  })
  const { action, token } = toRefs(props)

  const route = useRoute()
  const store = useStore()

  const { appConfig, appLanguage, displayOptions, errorMessages } = useApp()
  const { authUserSuccess } = useAuthUser()

  const formData: Reactive<ILoginRegisterFormData> = reactive({
    username: '',
    email: '',
    password: '',
    accepted_policy: false,
  })
  const formErrors: Ref<boolean> = ref(false)

  const buttonText: ComputedRef<string> = computed(() =>
    getButtonText(props.action)
  )
  const isRegistrationSuccess: ComputedRef<boolean> = computed(
    () => store.getters[AUTH_USER_STORE.GETTERS.IS_REGISTRATION_SUCCESS]
  )
  const registration_disabled: ComputedRef<boolean> = computed(
    () =>
      props.action === 'register' && !appConfig.value.is_registration_enabled
  )
  const sendingEmailDisabled: ComputedRef<boolean> = computed(
    () =>
      ['reset-request', 'account-confirmation-resend'].includes(props.action) &&
      !appConfig.value.is_email_sending_enabled
  )

  function getButtonText(action: string): string {
    switch (action) {
      case 'reset-request':
      case 'reset':
        return 'buttons.SUBMIT'
      default:
        return `buttons.${props.action.toUpperCase()}`
    }
  }
  function invalidateForm() {
    formErrors.value = true
  }
  function updatePassword(password: string) {
    formData.password = password
  }
  function onSubmit(actionType: string) {
    switch (actionType) {
      case 'reset':
        if (!token.value) {
          return store.commit(
            ROOT_STORE.MUTATIONS.SET_ERROR_MESSAGES,
            'user.INVALID_TOKEN'
          )
        }
        return store.dispatch(AUTH_USER_STORE.ACTIONS.RESET_USER_PASSWORD, {
          password: formData.password,
          token: String(token.value),
        })
      case 'reset-request':
        return store.dispatch(
          AUTH_USER_STORE.ACTIONS.SEND_PASSWORD_RESET_REQUEST,
          {
            email: formData.email,
          }
        )
      case 'account-confirmation-resend':
        return store.dispatch(
          AUTH_USER_STORE.ACTIONS.RESEND_ACCOUNT_CONFIRMATION_EMAIL,
          {
            email: formData.email,
          }
        )
      default:
        formData['language'] = appLanguage.value
        formData['timezone'] = displayOptions.value.timezone
        store.dispatch(AUTH_USER_STORE.ACTIONS.LOGIN_OR_REGISTER, {
          actionType,
          formData,
          redirectUrl: route.query.from,
        })
    }
  }
  function resetFormData() {
    formData.username = ''
    formData.email = ''
    formData.password = ''
    formData.accepted_policy = false
  }

  watch(
    () => route.path,
    async () => {
      store.commit(ROOT_STORE.MUTATIONS.EMPTY_ERROR_MESSAGES)
      store.commit(AUTH_USER_STORE.MUTATIONS.UPDATE_IS_SUCCESS, false)
      store.commit(
        AUTH_USER_STORE.MUTATIONS.UPDATE_IS_REGISTRATION_SUCCESS,
        false
      )
      formErrors.value = false
      resetFormData()
    }
  )
</script>

<style scoped lang="scss">
  @use '~@/scss/colors.scss' as *;
  @use '~@/scss/vars.scss' as *;

  #user-auth-form {
    display: flex;

    #user-form {
      width: 60%;

      .account {
        font-size: 0.9em;
        padding-left: $default-padding;
      }
      .links {
        font-size: 0.9em;
        font-style: italic;
        padding: 0 $default-padding;
      }
      button {
        margin: $default-margin;
        border: solid 1px var(--app-color);

        &:disabled {
          border-color: var(--disabled-color);
        }
      }
      .success-message {
        margin: $default-margin;
      }
      .accepted_policy {
        display: flex;
        align-items: center;
        font-size: 0.85em;
        font-weight: normal;
      }
      .form-items {
        label {
          padding-left: $default-padding;
          &.accepted_policy {
            padding-left: 0;
            input {
              margin-top: $default-margin;
            }
          }
        }
        ::v-deep(input) {
          margin-top: 0;
        }
        ::v-deep(.password-strength) {
          input {
            margin-top: $default-margin;
          }
        }
      }

      .form-info {
        margin-bottom: $default-padding * 0.5;
      }
    }

    @media screen and (max-width: $medium-limit) {
      margin-bottom: 50px;
      #user-form {
        width: 100%;
      }
    }
  }

  .user-form {
    margin-top: 200px;
    @media screen and (max-width: $small-limit) {
      margin-top: $default-margin;
    }
  }
</style>
