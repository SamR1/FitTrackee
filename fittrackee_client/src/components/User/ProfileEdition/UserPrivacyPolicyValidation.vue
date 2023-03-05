<template>
  <div id="user-privacy-policy">
    <ErrorMessage :message="errorMessages" v-if="errorMessages" />
    <div v-if="user.accepted_privacy_policy">
      <p>
        <i18n-t keypath="user.YOU_HAVE_ACCEPTED_PRIVACY_POLICY">
          <router-link to="/privacy-policy">
            {{ $t('privacy_policy.TITLE') }}
          </router-link>
        </i18n-t>
      </p>
      <button class="cancel" @click="$router.push('/profile')">
        {{ $t('user.PROFILE.BACK_TO_PROFILE') }}
      </button>
    </div>
    <form v-else @submit.prevent="onSubmit()">
      <div class="policy-content">
        <PrivacyPolicy />
      </div>
      <label
        for="accepted_policy"
        class="accepted_policy"
      >
        <input
          type="checkbox"
          id="accepted_policy"
          required
          v-model="acceptedPolicy"
        />
        <span>
          <i18n-t keypath="user.READ_AND_ACCEPT_PRIVACY_POLICY">
            {{ $t('privacy_policy.TITLE') }}
          </i18n-t>
        </span>
      </label>
      <router-link to="/profile/edit/account">
        {{ $t('user.I_WANT_TO_DELETE_MY_ACCOUNT') }}
      </router-link>
      <div class="form-buttons">
        <button class="confirm" type="submit">
          {{ $t('buttons.SUBMIT') }}
        </button>
        <button class="cancel" @click="$router.push('/profile')">
          {{ $t('user.PROFILE.BACK_TO_PROFILE') }}
        </button>
      </div>
    </form>
  </div>
</template>

<script setup lang="ts">
  import { ComputedRef, computed, ref, onUnmounted, toRefs } from 'vue'

  import PrivacyPolicy from '@/components/PrivacyPolicy.vue'
  import {AUTH_USER_STORE, ROOT_STORE} from '@/store/constants'
  import { IAuthUserProfile } from '@/types/user'
  import { useStore } from '@/use/useStore'

  interface Props {
    user: IAuthUserProfile
  }
  const props = defineProps<Props>()
  const { user } = toRefs(props)

  const store = useStore()

  const errorMessages: ComputedRef<string | string[] | null> = computed(
    () => store.getters[ROOT_STORE.GETTERS.ERROR_MESSAGES]
  )
  const acceptedPolicy= ref(false)

  function onSubmit() {
    store.dispatch(
        AUTH_USER_STORE.ACTIONS.ACCEPT_PRIVACY_POLICY, acceptedPolicy.value
    )
  }

  onUnmounted(() => {
    store.commit(ROOT_STORE.MUTATIONS.EMPTY_ERROR_MESSAGES)
  })
</script>

<style lang="scss" scoped>
  @import '~@/scss/vars.scss';

  #user-privacy-policy {
    padding: $default-padding 0;

    form {
      display: flex;
      flex-direction: column;
      gap: $default-padding;

      .policy-content {
        height: 500px;
        border:1px solid #ccc;
        overflow: auto;
        margin: $default-margin;
        border-radius: $border-radius;

        @media screen and (max-width: $small-limit) {
          margin: $default-margin 0;
          font-size:  .9em;
        }

        .privacy-policy-text {
          width: auto;
        }
      }

      .form-buttons {
        display: flex;
        gap: $default-padding;
        flex-direction: row;
        @media screen and (max-width: $x-small-limit) {
          flex-direction: column;
        }
      }
    }
  }
</style>
