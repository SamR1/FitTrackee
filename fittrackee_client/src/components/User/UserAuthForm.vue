<template>
  <div id="user-auth-form">
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
        <form @submit.prevent="onSubmit(action)">
          <div class="form-items">
            <input
              v-if="action === 'register'"
              id="username"
              :disabled="registration_disabled"
              required
              v-model="formData.username"
              :placeholder="$t('user.USERNAME')"
            />
            <input
              v-if="action !== 'reset'"
              id="email"
              :disabled="registration_disabled"
              required
              type="email"
              v-model="formData.email"
              :placeholder="
                action === 'reset-request'
                  ? $t('user.ENTER_EMAIL')
                  : $t('user.EMAIL')
              "
            />
            <input
              v-if="action !== 'reset-request'"
              id="password"
              :disabled="registration_disabled"
              required
              type="password"
              v-model="formData.password"
              :placeholder="
                action === 'reset'
                  ? $t('user.ENTER_PASSWORD')
                  : $t('user.PASSWORD')
              "
            />
            <input
              v-if="['register', 'reset'].includes(action)"
              id="confirm-password"
              :disabled="registration_disabled"
              type="password"
              required
              v-model="formData.password_conf"
              :placeholder="
                action === 'reset'
                  ? $t('user.ENTER_PASSWORD_CONFIRMATION')
                  : $t('user.PASSWORD_CONFIRM')
              "
            />
          </div>
          <button type="submit" :disabled="registration_disabled">
            {{ $t(buttonText) }}
          </button>
        </form>
        <div v-if="action === 'login'">
          <router-link class="password-forgotten" to="/password-reset/request">
            {{ $t('user.PASSWORD_FORGOTTEN') }}
          </router-link>
        </div>
        <ErrorMessage :message="errorMessages" v-if="errorMessages" />
      </div>
    </div>
  </div>
</template>

<script lang="ts">
  import { ComputedRef, computed, defineComponent, reactive, watch } from 'vue'
  import { useRoute } from 'vue-router'

  import { ROOT_STORE, USER_STORE } from '@/store/constants'
  import { TAppConfig } from '@/types/application'
  import { ILoginRegisterFormData } from '@/types/user'
  import { useStore } from '@/use/useStore'

  export default defineComponent({
    name: 'UserAuthForm',
    props: {
      action: {
        type: String,
        required: true,
      },
      token: {
        type: String,
        default: '',
      },
    },
    setup(props) {
      const formData: ILoginRegisterFormData = reactive({
        username: '',
        email: '',
        password: '',
        password_conf: '',
      })
      const route = useRoute()
      const store = useStore()

      const buttonText: ComputedRef<string> = computed(() =>
        getButtonText(props.action)
      )
      const errorMessages: ComputedRef<string | string[] | null> = computed(
        () => store.getters[ROOT_STORE.GETTERS.ERROR_MESSAGES]
      )
      const appConfig: ComputedRef<TAppConfig> = computed(
        () => store.getters[ROOT_STORE.GETTERS.APP_CONFIG]
      )
      const registration_disabled: ComputedRef<boolean> = computed(
        () =>
          props.action === 'register' &&
          !appConfig.value.is_registration_enabled
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
      function onSubmit(actionType: string) {
        switch (actionType) {
          case 'reset':
            if (!props.token) {
              return store.commit(
                ROOT_STORE.MUTATIONS.SET_ERROR_MESSAGES,
                'user.INVALID_TOKEN'
              )
            }
            return store.dispatch(USER_STORE.ACTIONS.RESET_USER_PASSWORD, {
              password: formData.password,
              password_conf: formData.password_conf,
              token: props.token,
            })
          case 'reset-request':
            return store.dispatch(
              USER_STORE.ACTIONS.SEND_PASSWORD_RESET_REQUEST,
              {
                email: formData.email,
              }
            )
          default:
            store.dispatch(USER_STORE.ACTIONS.LOGIN_OR_REGISTER, {
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
        formData.password_conf = ''
      }
      watch(
        () => route.path,
        async () => {
          store.commit(ROOT_STORE.MUTATIONS.EMPTY_ERROR_MESSAGES)
          resetFormData()
        }
      )
      return {
        appConfig,
        buttonText,
        errorMessages,
        formData,
        registration_disabled,
        onSubmit,
      }
    },
  })
</script>

<style scoped lang="scss">
  @import '~@/scss/base';

  #user-auth-form {
    display: flex;
    align-items: center;

    margin: $default-margin 0;
    height: 100%;

    #user-form {
      width: 60%;

      .password-forgotten {
        font-size: 0.9em;
        font-style: italic;
        padding-left: $default-padding;
      }

      button {
        margin: $default-margin;
        border: solid 1px var(--app-color);

        &:disabled {
          border-color: var(--disabled-color);
        }
      }
    }

    @media screen and (max-width: $medium-limit) {
      height: auto;
      margin-bottom: 50px;

      #user-form {
        margin-top: $default-margin;
        width: 100%;
      }
    }
  }
</style>
