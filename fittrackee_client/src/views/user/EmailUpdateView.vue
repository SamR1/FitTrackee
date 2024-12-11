<template>
  <div
    id="email-update"
    class="center-card with-margin"
    v-if="errorMessages && !authUser.username"
  >
    <ErrorImg />
    <p class="error-message">
      <span>{{ $t('error.SOMETHING_WRONG') }}.</span>
      <span>
        <i18n-t keypath="user.PROFILE.ERRORED_EMAIL_UPDATE">
          <router-link to="/login">
            {{ $t('user.LOG_IN') }}
          </router-link>
        </i18n-t>
      </span>
    </p>
  </div>
</template>

<script setup lang="ts">
  import { onBeforeMount, watch } from 'vue'
  import { useRouter } from 'vue-router'

  import ErrorImg from '@/components/Common/Images/ErrorImg.vue'
  import useApp from '@/composables/useApp'
  import useAuthUser from '@/composables/useAuthUser'
  import { AUTH_USER_STORE } from '@/store/constants'
  import { useStore } from '@/use/useStore'

  const router = useRouter()
  const store = useStore()

  const { errorMessages } = useApp()
  const { authUser, isAuthenticated, token } = useAuthUser()

  function confirmEmail() {
    if (token.value) {
      store.dispatch(AUTH_USER_STORE.ACTIONS.CONFIRM_EMAIL, {
        token: token.value,
        refreshUser: isAuthenticated.value,
      })
    } else {
      router.push('/')
    }
  }

  watch(
    () => errorMessages.value,
    (newValue) => {
      if (authUser.value.username && newValue) {
        router.push('/')
      }
    }
  )

  onBeforeMount(() => confirmEmail())
</script>

<style lang="scss" scoped>
  @import '~@/scss/vars.scss';

  #email-update {
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
