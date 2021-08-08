<template>
  <div id="user-form">
    <div class="form-box">
      <form @submit.prevent="onSubmit(action)">
        <div class="form-items">
          <input
            v-if="action === 'register'"
            id="username"
            required
            v-model="user.username"
            :placeholder="t('user.REGISTER')"
          />
          <input
            id="email"
            required
            type="email"
            v-model="user.email"
            :placeholder="t('user.EMAIL')"
          />
          <input
            id="password"
            required
            type="password"
            v-model="user.password"
            :placeholder="t('user.PASSWORD')"
          />
          <input
            v-if="action === 'register'"
            id="confirm-password"
            type="password"
            required
            v-model="user.confirmPassword"
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
      const user = reactive({
        username: '',
        email: '',
        password: '',
        confirmPassword: '',
      })
      const { t } = useI18n()
      function onSubmit(action: string) {
        console.log(action, user)
      }

      return {
        errorMessage: ref(null),
        t,
        user,
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
