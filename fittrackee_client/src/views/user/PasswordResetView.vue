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
  import { computed, toRefs, onBeforeMount } from 'vue'
  import { useRoute, useRouter } from 'vue-router'

  import PasswordEmailSent from '@/components/User/PasswordReset/PasswordActionDone.vue'
  import PasswordResetRequest from '@/components/User/PasswordReset/PasswordResetForm.vue'

  interface Props {
    action: string
  }
  const props = defineProps<Props>()

  const route = useRoute()
  const router = useRouter()

  const { action } = toRefs(props)
  const token = computed(() => route.query.token)

  onBeforeMount(() => {
    if (props.action === 'reset' && !token.value) {
      router.push('/')
    }
  })
</script>

<style lang="scss" scoped>
  @import '~@/scss/vars.scss';

  #password-reset {
    display: flex;
    .container {
      display: flex;
      justify-content: center;
      width: 50%;

      @media screen and (max-width: $small-limit) {
        width: 100%;
        margin: 0 auto 50px auto;
      }
    }
  }
</style>
