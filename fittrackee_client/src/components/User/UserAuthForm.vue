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
        <form
          :class="{ errors: formErrors }"
          @submit.prevent="onSubmit(action)"
        >
          <div class="form-items">
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
              :placeholder="$t('user.USERNAME')"
            />
            <input
              v-if="action !== 'reset'"
              id="email"
              :disabled="registration_disabled"
              required
              @invalid="invalidateForm"
              type="email"
              v-model="formData.email"
              :placeholder="
                action === 'reset-request'
                  ? $t('user.ENTER_EMAIL')
                  : $t('user.EMAIL')
              "
            />
            <PasswordInput
              v-if="action !== 'reset-request'"
              :disabled="registration_disabled"
              :required="true"
              :placeholder="
                action === 'reset'
                  ? $t('user.ENTER_PASSWORD')
                  : $t('user.PASSWORD')
              "
              @updatePassword="updatePassword"
              @passwordError="invalidateForm"
            />
          </div>
          <button type="submit" :disabled="registration_disabled">
            {{ $t(buttonText) }}
          </button>
        </form>
        <div v-if="action === 'login'">
          <router-link class="links" to="/register">
            {{ $t('user.REGISTER') }}
          </router-link>
          -
          <router-link class="links" to="/password-reset/request">
            {{ $t('user.PASSWORD_FORGOTTEN') }}
          </router-link>
        </div>
        <div v-if="action === 'register'">
          <span class="account">{{ $t('user.ALREADY_HAVE_ACCOUNT') }}</span>
          <router-link class="links" to="/login">
            {{ $t('user.LOGIN') }}
          </router-link>
        </div>
        <ErrorMessage :message="errorMessages" v-if="errorMessages" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
  import {
    ComputedRef,
    computed,
    reactive,
    ref,
    toRefs,
    watch,
    withDefaults,
  } from 'vue'
  import { useRoute } from 'vue-router'

  import PasswordInput from '@/components/Common/PasswordInput.vue'
  import { AUTH_USER_STORE, ROOT_STORE } from '@/store/constants'
  import { TAppConfig } from '@/types/application'
  import { ILoginRegisterFormData } from '@/types/user'
  import { useStore } from '@/use/useStore'

  interface Props {
    action: string
    token?: string
  }
  const props = withDefaults(defineProps<Props>(), {
    token: '',
  })

  const route = useRoute()
  const store = useStore()

  const { action } = toRefs(props)
  const formData: ILoginRegisterFormData = reactive({
    username: '',
    email: '',
    password: '',
  })
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
      props.action === 'register' && !appConfig.value.is_registration_enabled
  )
  const formErrors = ref(false)

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
        if (!props.token) {
          return store.commit(
            ROOT_STORE.MUTATIONS.SET_ERROR_MESSAGES,
            'user.INVALID_TOKEN'
          )
        }
        return store.dispatch(AUTH_USER_STORE.ACTIONS.RESET_USER_PASSWORD, {
          password: formData.password,
          token: props.token,
        })
      case 'reset-request':
        return store.dispatch(
          AUTH_USER_STORE.ACTIONS.SEND_PASSWORD_RESET_REQUEST,
          {
            email: formData.email,
          }
        )
      default:
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
  }

  watch(
    () => route.path,
    async () => {
      store.commit(ROOT_STORE.MUTATIONS.EMPTY_ERROR_MESSAGES)
      formErrors.value = false
      resetFormData()
    }
  )
</script>

<style scoped lang="scss">
  @import '~@/scss/colors.scss';
  @import '~@/scss/vars.scss';

  #user-auth-form {
    display: flex;
    align-items: center;

    margin: $default-margin 0;
    height: 100%;

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
