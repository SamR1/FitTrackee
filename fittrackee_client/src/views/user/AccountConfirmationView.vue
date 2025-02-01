<template>
  <div
    id="account-confirmation"
    class="center-card with-margin"
    v-if="errorMessages"
  >
    <ErrorImg />
    <p class="error-message">
      <span>{{ $t('error.SOMETHING_WRONG') }}.</span>
      <router-link class="links" to="/account-confirmation/resend">
        {{ $t('buttons.ACCOUNT-CONFIRMATION-RESEND') }}?
      </router-link>
    </p>
  </div>
</template>

<script setup lang="ts">
  import { onBeforeMount } from 'vue'
  import { useRouter } from 'vue-router'

  import ErrorImg from '@/components/Common/Images/ErrorImg.vue'
  import useApp from '@/composables/useApp'
  import useAuthUser from '@/composables/useAuthUser'
  import { AUTH_USER_STORE } from '@/store/constants'
  import { useStore } from '@/use/useStore'

  const router = useRouter()
  const store = useStore()

  const { errorMessages } = useApp()
  const { token } = useAuthUser()

  function confirmAccount() {
    if (token.value) {
      store.dispatch(AUTH_USER_STORE.ACTIONS.CONFIRM_ACCOUNT, {
        token: token.value,
      })
    } else {
      router.push('/')
    }
  }

  onBeforeMount(() => confirmAccount())
</script>

<style lang="scss" scoped>
  @use '~@/scss/vars.scss' as *;

  #account-confirmation {
    display: flex;
    flex-direction: column;
    align-items: center;

    svg {
      stroke: none;
      fill-rule: nonzero;
      fill: var(--app-color);
      filter: var(--svg-filter);
      width: 100px;
    }

    .error-message {
      font-size: 1.1em;
      text-align: center;
      display: flex;
      flex-direction: column;

      @media screen and (max-width: $medium-limit) {
        font-size: 1em;
      }
    }
  }
</style>
