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
  import { computed, onBeforeMount, onUnmounted, watch } from 'vue'
  import type { ComputedRef } from 'vue'
  import { useRoute, useRouter } from 'vue-router'
  import type { LocationQueryValue } from 'vue-router'

  import ErrorImg from '@/components/Common/Images/ErrorImg.vue'
  import { AUTH_USER_STORE, ROOT_STORE } from '@/store/constants'
  import type { IAuthUserProfile } from '@/types/user'
  import { useStore } from '@/use/useStore'

  const route = useRoute()
  const router = useRouter()
  const store = useStore()

  const authUser: ComputedRef<IAuthUserProfile> = computed(
    () => store.getters[AUTH_USER_STORE.GETTERS.AUTH_USER_PROFILE]
  )
  const isAuthenticated: ComputedRef<boolean> = computed(
    () => store.getters[AUTH_USER_STORE.GETTERS.IS_AUTHENTICATED]
  )
  const errorMessages: ComputedRef<string | string[] | null> = computed(
    () => store.getters[ROOT_STORE.GETTERS.ERROR_MESSAGES]
  )
  const token: ComputedRef<LocationQueryValue | LocationQueryValue[]> =
    computed(() => route.query.token)

  onBeforeMount(() => confirmEmail())

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

  onUnmounted(() => store.commit(ROOT_STORE.MUTATIONS.EMPTY_ERROR_MESSAGES))

  watch(
    () => errorMessages.value,
    (newValue) => {
      if (authUser.value.username && newValue) {
        router.push('/')
      }
    }
  )
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
