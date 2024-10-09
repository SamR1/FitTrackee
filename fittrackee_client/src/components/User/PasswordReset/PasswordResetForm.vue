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

<script setup lang="ts">
  import { toRefs } from 'vue'

  import UserAuthForm from '@/components/User/UserAuthForm.vue'
  import type { TToken } from '@/types/user'

  interface Props {
    action: string
    token?: TToken
  }
  const props = withDefaults(defineProps<Props>(), {
    token: '',
  })
  const { action, token } = toRefs(props)
</script>

<style scoped lang="scss">
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
