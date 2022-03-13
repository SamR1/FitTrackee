<template>
  <div id="user-infos-edition">
    <Modal
      v-if="displayModal"
      :title="$t('common.CONFIRMATION')"
      :message="$t('user.CONFIRM_ACCOUNT_DELETION')"
      @confirmAction="deleteAccount(user.username)"
      @cancelAction="updateDisplayModal(false)"
    />
    <div class="profile-form form-box">
      <ErrorMessage :message="errorMessages" v-if="errorMessages" />
      <div class="info-box success-message" v-if="isSuccess">
        {{ $t('user.PROFILE.SUCCESSFUL_UPDATE') }}
      </div>
      <form :class="{ errors: formErrors }" @submit.prevent="updateProfile">
        <label class="form-items" for="email">
          {{ $t('user.EMAIL') }}
          <input id="email" :value="user.email" disabled />
        </label>
        <label class="form-items" for="password-field">
          {{ $t('user.CURRENT_PASSWORD') }}*
          <PasswordInput
            id="password-field"
            :disabled="loading"
            :password="userForm.password"
            :required="true"
            @updatePassword="updatePassword"
            @passwordError="invalidateForm"
          />
        </label>
        <label class="form-items" for="new-password-field">
          {{ $t('user.NEW_PASSWORD') }}*
          <PasswordInput
            id="new-password-field"
            :disabled="loading"
            :checkStrength="true"
            :password="userForm.new_password"
            :isSuccess="false"
            :required="true"
            @updatePassword="updateNewPassword"
            @passwordError="invalidateForm"
          />
        </label>
        <div class="form-buttons">
          <button class="confirm" type="submit">
            {{ $t('buttons.SUBMIT') }}
          </button>
          <button class="cancel" @click.prevent="$router.push('/profile')">
            {{ $t('buttons.CANCEL') }}
          </button>
          <button class="danger" @click.prevent="updateDisplayModal(true)">
            {{ $t('buttons.DELETE_MY_ACCOUNT') }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
  import {
    ComputedRef,
    Ref,
    computed,
    reactive,
    ref,
    toRefs,
    onMounted,
    watch,
    onUnmounted,
  } from 'vue'

  import PasswordInput from '@/components/Common/PasswordInput.vue'
  import { AUTH_USER_STORE, ROOT_STORE } from '@/store/constants'
  import { IUserProfile, IUserAccountPayload } from '@/types/user'
  import { useStore } from '@/use/useStore'

  interface Props {
    user: IUserProfile
  }
  const props = defineProps<Props>()
  const { user } = toRefs(props)

  const store = useStore()
  const userForm: IUserAccountPayload = reactive({
    email: '',
    password: '',
    new_password: '',
  })
  const loading = computed(
    () => store.getters[AUTH_USER_STORE.GETTERS.USER_LOADING]
  )
  const isSuccess: ComputedRef<boolean> = computed(
    () => store.getters[AUTH_USER_STORE.GETTERS.IS_SUCCESS]
  )
  const errorMessages: ComputedRef<string | string[] | null> = computed(
    () => store.getters[ROOT_STORE.GETTERS.ERROR_MESSAGES]
  )
  const formErrors = ref(false)
  const displayModal: Ref<boolean> = ref(false)

  onMounted(() => {
    if (props.user) {
      updateUserForm(props.user)
    }
  })

  function invalidateForm() {
    formErrors.value = true
  }
  function updateUserForm(user: IUserProfile) {
    userForm.email = user.email
  }
  function updatePassword(password: string) {
    userForm.password = password
  }
  function updateNewPassword(new_password: string) {
    userForm.new_password = new_password
  }
  function updateProfile() {
    store.dispatch(AUTH_USER_STORE.ACTIONS.UPDATE_USER_ACCOUNT, {
      password: userForm.password,
      new_password: userForm.new_password,
    })
  }
  function updateDisplayModal(value: boolean) {
    displayModal.value = value
  }
  function deleteAccount(username: string) {
    store.dispatch(AUTH_USER_STORE.ACTIONS.DELETE_ACCOUNT, { username })
  }

  onUnmounted(() => {
    store.commit(AUTH_USER_STORE.MUTATIONS.UPDATE_IS_SUCCESS, false)
    store.commit(ROOT_STORE.MUTATIONS.EMPTY_ERROR_MESSAGES)
  })

  watch(
    () => isSuccess.value,
    async (isSuccessValue) => {
      if (isSuccessValue) {
        updatePassword('')
        updateNewPassword('')
        formErrors.value = false
      }
    }
  )
</script>

<style lang="scss" scoped>
  @import '~@/scss/vars.scss';

  .form-items {
    .password-input {
      ::v-deep(.show-password) {
        font-weight: normal;
        font-size: 0.8em;
        margin-top: -4px;
        padding-left: 0;
      }
      ::v-deep(.form-info) {
        font-weight: normal;
        padding-left: $default-padding;
      }
      ::v-deep(.password-strength-details) {
        font-weight: normal;
        margin-top: 0;
      }
    }
  }

  .form-buttons {
    flex-direction: row;
    @media screen and (max-width: $x-small-limit) {
      flex-direction: column;
    }
  }

  .success-message {
    margin: $default-margin * 2 0;
    background-color: var(--success-background-color);
    color: var(--success-color);
  }
</style>
