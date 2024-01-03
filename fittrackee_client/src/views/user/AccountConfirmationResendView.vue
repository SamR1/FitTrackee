<template>
  <div id="account-confirmation" class="view">
    <div class="container">
      <AccountConfirmationResend :action="action" />
    </div>
  </div>
</template>

<script setup lang="ts">
  import { toRefs } from 'vue'

  import AccountConfirmationResend from '@/components/User/AccountConfirmationEmail.vue'
  interface Props {
    action: string
  }
  const props = defineProps<Props>()
  const { action } = toRefs(props)
</script>

<style lang="scss" scoped>
  @import '~@/scss/vars.scss';

  #account-confirmation {
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
