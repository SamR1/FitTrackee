<template>
  <div id="login-form">
    <div id="user-form">
      <div class="form-box">
        <form @submit.prevent="onSubmit(action)">
          <div class="form-items">
            <input
              v-if="action === 'register'"
              id="username"
              required
              v-model="formData.username"
              :placeholder="t('user.USERNAME')"
            />
            <input
              id="email"
              required
              type="email"
              v-model="formData.email"
              :placeholder="t('user.EMAIL')"
            />
            <input
              id="password"
              required
              type="password"
              v-model="formData.password"
              :placeholder="t('user.PASSWORD')"
            />
            <input
              v-if="action === 'register'"
              id="confirm-password"
              type="password"
              required
              v-model="formData.password_conf"
              :placeholder="t('user.PASSWORD-CONFIRM')"
            />
          </div>
          <button type="submit">{{ t(buttonText) }}</button>
        </form>
        <p v-if="errorMessage">
          {{ errorMessage }}
        </p>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
  import { ComputedRef, computed, defineComponent, reactive } from 'vue'
  import { useI18n } from 'vue-i18n'

  import { IFormData } from '@/interfaces'
  import { ROOT_STORE, USER_STORE } from '@/store/constants'
  import { useStore } from '@/use/useStore'

  export default defineComponent({
    name: 'LoginForm',
    props: {
      action: {
        type: String,
        required: true,
      },
    },
    setup(props) {
      const formData: IFormData = reactive({
        username: '',
        email: '',
        password: '',
        password_conf: '',
      })
      const { t } = useI18n()
      const store = useStore()

      const buttonText: ComputedRef<string> = computed(() =>
        props.action === 'register' ? 'buttons.REGISTER' : 'buttons.LOGIN'
      )
      const errorMessage: ComputedRef<string | null> = computed(
        () => store.getters[ROOT_STORE.GETTERS.ERROR_MESSAGE]
      )

      function onSubmit(actionType: string) {
        return store.dispatch(USER_STORE.ACTIONS.LOGIN_OR_REGISTER, {
          actionType,
          formData,
        })
      }

      return {
        t,
        buttonText,
        errorMessage,
        formData,
        onSubmit,
      }
    },
  })
</script>

<style scoped lang="scss">
  @import '~@/scss/base';

  #login-form {
    display: flex;
    align-items: center;

    margin: $default-margin 0;
    height: 100%;

    #user-form {
      width: 60%;

      button {
        margin: $default-margin;
      }
      @media screen and (max-width: $medium-limit) {
        margin-top: $default-margin;
        width: 100%;
      }
    }

    @media screen and (max-width: $medium-limit) {
      height: auto;
    }
  }
</style>
