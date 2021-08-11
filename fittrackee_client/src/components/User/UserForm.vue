<template>
  <div id="user-form">
    <div class="form-box">
      <form @submit.prevent="onSubmit(action)">
        <div class="form-items">
          <input
            v-if="action === 'register'"
            id="username"
            required
            v-model="formData.username"
            :placeholder="t('user.REGISTER')"
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
            v-model="formData.confirmPassword"
            :placeholder="t('user.PASSWORD-CONFIRM')"
          />
        </div>
        <button type="submit">{{ t('buttons.LOGIN') }}</button>
      </form>
      <p v-if="errorMessage">
        {{ errorMessage }}
      </p>
    </div>
  </div>
</template>

<script lang="ts">
  import { defineComponent, reactive, ref } from 'vue'
  import { useI18n } from 'vue-i18n'
  import { useStore } from 'vuex'
  import { IFormData } from '@/interfaces.ts'
  import { USER_STORE } from '@/store/constants'

  export default defineComponent({
    name: 'UserForm',
    components: {},
    props: {
      action: {
        type: String,
        required: true,
      },
    },
    setup() {
      const formData: IFormData = reactive({
        username: '',
        email: '',
        password: '',
        confirmPassword: '',
      })
      const { t } = useI18n()
      const store = useStore()
      function onSubmit(actionType: string) {
        return store.dispatch(USER_STORE.ACTIONS.LOGIN_OR_REGISTER, {
          actionType,
          formData,
        })
      }

      return {
        errorMessage: ref(null),
        t,
        formData,
        onSubmit,
      }
    },
  })
</script>

<style scoped lang="scss">
  @import '~@/scss/base';

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
</style>
