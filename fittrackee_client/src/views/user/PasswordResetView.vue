<template>
  <div id="password-reset" class="view">
    <div class="container">
      <PasswordResetRequest
        v-if="action.startsWith('reset')"
        :action="action"
        :token="token"
      />
      <PasswordEmailSent v-else :action="action" />
    </div>
  </div>
</template>

<script setup lang="ts">
  import { toRefs, onBeforeMount } from 'vue'
  import { useRouter } from 'vue-router'

  import PasswordEmailSent from '@/components/User/PasswordReset/PasswordActionDone.vue'
  import PasswordResetRequest from '@/components/User/PasswordReset/PasswordResetForm.vue'
  import useAuthUser from '@/composables/useAuthUser'

  interface Props {
    action: string
  }
  const props = defineProps<Props>()
  const { action } = toRefs(props)

  const router = useRouter()

  const { token } = useAuthUser()

  onBeforeMount(() => {
    if (props.action === 'reset' && !token.value) {
      router.push('/')
    }
  })
</script>

<style lang="scss" scoped>
  @use '~@/scss/vars.scss' as *;

  #password-reset {
    display: flex;
    .container {
      display: flex;
      justify-content: center;
      width: 50%;

      @media screen and (max-width: $small-limit) {
        width: 100%;
      }
    }
  }
</style>
