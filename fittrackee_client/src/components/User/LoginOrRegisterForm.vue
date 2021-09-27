<template>
  <div id="login-or-register-form">
    <div id="user-form">
      <div
        class="form-box"
        :class="{
          disabled: registration_disabled,
        }"
      >
        <form @submit.prevent="onSubmit(action)">
          <div class="form-items">
            <input
              v-if="action === 'register'"
              id="username"
              :disabled="registration_disabled"
              required
              v-model="formData.username"
              :placeholder="t('user.USERNAME')"
            />
            <input
              id="email"
              :disabled="registration_disabled"
              required
              type="email"
              v-model="formData.email"
              :placeholder="t('user.EMAIL')"
            />
            <input
              id="password"
              :disabled="registration_disabled"
              required
              type="password"
              v-model="formData.password"
              :placeholder="t('user.PASSWORD')"
            />
            <input
              v-if="action === 'register'"
              id="confirm-password"
              :disabled="registration_disabled"
              type="password"
              required
              v-model="formData.password_conf"
              :placeholder="t('user.PASSWORD-CONFIRM')"
            />
          </div>
          <button type="submit" :disabled="registration_disabled">
            {{ t(buttonText) }}
          </button>
        </form>
        <ErrorMessage :message="errorMessages" v-if="errorMessages" />
        <AlertMessage
          message="user.REGISTER_DISABLED"
          v-if="registration_disabled"
        />
      </div>
    </div>
  </div>
</template>

<script lang="ts">
  import { ComputedRef, computed, defineComponent, reactive, watch } from 'vue'
  import { useI18n } from 'vue-i18n'
  import { useRoute } from 'vue-router'

  import AlertMessage from '@/components/Common/AlertMessage.vue'
  import ErrorMessage from '@/components/Common/ErrorMessage.vue'
  import router from '@/router'
  import { ROOT_STORE, USER_STORE } from '@/store/constants'
  import { IAppConfig } from '@/types/application'
  import { ILoginRegisterFormData } from '@/types/user'
  import { useStore } from '@/use/useStore'

  export default defineComponent({
    name: 'LoginOrRegisterForm',
    components: {
      AlertMessage,
      ErrorMessage,
    },
    props: {
      action: {
        type: String,
        required: true,
      },
    },
    setup(props) {
      const formData: ILoginRegisterFormData = reactive({
        username: '',
        email: '',
        password: '',
        password_conf: '',
      })
      const { t } = useI18n()
      const route = useRoute()
      const store = useStore()

      const buttonText: ComputedRef<string> = computed(() =>
        props.action === 'register' ? 'buttons.REGISTER' : 'buttons.LOGIN'
      )
      const errorMessages: ComputedRef<string | string[] | null> = computed(
        () => store.getters[ROOT_STORE.GETTERS.ERROR_MESSAGES]
      )
      const appConfig: ComputedRef<IAppConfig> = computed(
        () => store.getters[ROOT_STORE.GETTERS.APP_CONFIG]
      )
      const registration_disabled: ComputedRef<boolean> = computed(
        () =>
          props.action === 'register' &&
          !appConfig.value.is_registration_enabled
      )

      function onSubmit(actionType: string) {
        return store.dispatch(USER_STORE.ACTIONS.LOGIN_OR_REGISTER, {
          actionType,
          formData,
        })
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
        t,
        appConfig,
        buttonText,
        errorMessages,
        formData,
        onSubmit,
        registration_disabled,
        router,
      }
    },
  })
</script>

<style scoped lang="scss">
  @import '~@/scss/base';

  #login-or-register-form {
    display: flex;
    align-items: center;

    margin: $default-margin 0;
    height: 100%;

    #user-form {
      width: 60%;

      button {
        margin: $default-margin;
        border: solid 1px var(--app-color);

        &:disabled {
          border-color: var(--disabled-color);
        }
      }
      @media screen and (max-width: $medium-limit) {
        margin-top: $default-margin;
        width: 100%;
      }
    }

    @media screen and (max-width: $medium-limit) {
      height: auto;
      margin-bottom: 50px;
    }
  }
</style>
