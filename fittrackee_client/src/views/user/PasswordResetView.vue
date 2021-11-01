<template>
  <div id="password-reset">
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

<script lang="ts">
  import { computed, defineComponent, onBeforeMount } from 'vue'
  import { useRoute, useRouter } from 'vue-router'

  import PasswordEmailSent from '@/components/User/PasswordReset/PasswordActionDone.vue'
  import PasswordResetRequest from '@/components/User/PasswordReset/PasswordResetForm.vue'
  export default defineComponent({
    name: 'PasswordResetView',
    components: {
      PasswordEmailSent,
      PasswordResetRequest,
    },
    props: {
      action: {
        type: String,
        required: true,
      },
    },
    setup(props) {
      const route = useRoute()
      const router = useRouter()
      const token = computed(() => route.query.token)

      onBeforeMount(() => {
        if (props.action === 'reset' && !token.value) {
          router.push('/')
        }
      })

      return { token }
    },
  })
</script>

<style lang="scss" scoped>
  @import '~@/scss/base.scss';

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
