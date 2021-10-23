<template>
  <div id="password-reset-request" class="center-card with-margin">
    <Card>
      <template #title>{{ $t('user.RESET_PASSWORD') }}</template>
      <template #content>
        <UserAuthForm :action="action" :token="token" />
      </template>
    </Card>
  </div>
</template>

<script lang="ts">
  import { defineComponent } from 'vue'

  import UserAuthForm from '@/components/User/UserAuthForm.vue'

  export default defineComponent({
    name: 'PasswordResetForm',
    components: {
      UserAuthForm,
    },
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
  })
</script>

<style scoped lang="scss">
  @import '~@/scss/base';

  #password-reset-request {
    ::v-deep(.card) {
      .card-content {
        #user-form {
          width: 100%;
        }
      }
    }
  }
</style>
