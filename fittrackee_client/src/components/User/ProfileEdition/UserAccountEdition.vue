<template>
  <div id="user-account-edition">
    <Modal
      v-if="displayModal"
      :title="$t('common.CONFIRMATION')"
      :message="$t('user.CONFIRM_ACCOUNT_DELETION')"
      @confirmAction="deleteAccount(user.username)"
      @cancelAction="updateDisplayModal(false)"
      @keydown.esc="updateDisplayModal(false)"
    />
    <div class="form-box">
      <ErrorMessage :message="errorMessages" v-if="errorMessages" />
      <div class="info-box success-message" v-if="authUserSuccess">
        {{
          $t(
            `user.PROFILE.SUCCESSFUL_${
              emailUpdate && appConfig.is_email_sending_enabled ? 'EMAIL_' : ''
            }UPDATE`
          )
        }}
      </div>
      <form :class="{ errors: formErrors }" @submit.prevent="updateProfile">
        <label class="form-items" for="email">
          {{ $t('user.EMAIL') }}*
          <input
            id="email"
            v-model="userForm.email"
            :disabled="authUserLoading"
            :required="true"
            @invalid="invalidateForm"
            autocomplete="email"
          />
        </label>
        <label class="form-items" for="password-field">
          {{ $t('user.CURRENT_PASSWORD') }}*
          <PasswordInput
            id="password-field"
            :disabled="authUserLoading"
            :password="userForm.password"
            :required="true"
            @updatePassword="updatePassword"
            @passwordError="invalidateForm"
            autocomplete="current-password"
          />
        </label>
        <label class="form-items" for="new-password-field">
          {{ $t('user.NEW_PASSWORD') }}
          <PasswordInput
            id="new-password-field"
            :disabled="authUserLoading"
            :checkStrength="true"
            :password="userForm.new_password"
            :isSuccess="false"
            @updatePassword="updateNewPassword"
            @passwordError="invalidateForm"
            autocomplete="new-password"
          />
        </label>
        <div class="form-buttons">
          <button class="confirm" type="submit">
            {{ $t('buttons.SUBMIT') }}
          </button>
          <button
            class="cancel"
            @click.prevent="$router.push('/profile/account')"
          >
            {{ $t('buttons.CANCEL') }}
          </button>
          <button
            class="confirm"
            :disabled="!canRequestExport()"
            @click.prevent="requestExport"
          >
            {{ $t('buttons.REQUEST_DATA_EXPORT') }}
          </button>
          <button class="danger" @click.prevent="updateDisplayModal(true)">
            {{ $t('buttons.DELETE_MY_ACCOUNT') }}
          </button>
        </div>
      </form>
      <UserDataExport :user="user" />
    </div>
  </div>
</template>

<script setup lang="ts">
  import { reactive, ref, toRefs, onMounted, watch, onUnmounted } from 'vue'
  import type { Reactive, Ref } from 'vue'

  import PasswordInput from '@/components/Common/PasswordInput.vue'
  import UserDataExport from '@/components/User/UserDataExport.vue'
  import useApp from '@/composables/useApp'
  import useAuthUser from '@/composables/useAuthUser'
  import useUserDataExport from '@/composables/useUserDataExport'
  import { AUTH_USER_STORE } from '@/store/constants'
  import type { IAuthUserProfile, IUserAccountPayload } from '@/types/user'
  import { useStore } from '@/use/useStore'
  interface Props {
    user: IAuthUserProfile
  }
  const props = defineProps<Props>()
  const { user } = toRefs(props)

  const store = useStore()

  const { appConfig, errorMessages } = useApp()
  const { authUserLoading, authUserSuccess } = useAuthUser()
  const { canRequestExport, requestExport } = useUserDataExport()

  const userForm: Reactive<IUserAccountPayload> = reactive({
    email: '',
    password: '',
    new_password: '',
  })
  const emailUpdate: Ref<boolean> = ref(false)
  const formErrors: Ref<boolean> = ref(false)
  const displayModal: Ref<boolean> = ref(false)

  function invalidateForm() {
    formErrors.value = true
  }
  function updateUserForm(user: IAuthUserProfile) {
    userForm.email = user.email
  }
  function updatePassword(password: string) {
    userForm.password = password
  }
  function updateNewPassword(new_password: string) {
    userForm.new_password = new_password
  }
  function updateProfile() {
    const payload: IUserAccountPayload = {
      email: userForm.email,
      password: userForm.password,
    }
    if (userForm.new_password) {
      payload.new_password = userForm.new_password
    }
    emailUpdate.value = userForm.email !== user.value.email
    store.dispatch(AUTH_USER_STORE.ACTIONS.UPDATE_USER_ACCOUNT, payload)
  }
  function updateDisplayModal(value: boolean) {
    displayModal.value = value
  }
  function deleteAccount(username: string) {
    store.dispatch(AUTH_USER_STORE.ACTIONS.DELETE_ACCOUNT, { username })
  }

  watch(
    () => authUserSuccess.value,
    async (authUserSuccessValue) => {
      if (authUserSuccessValue) {
        updatePassword('')
        updateNewPassword('')
        updateUserForm(user.value)
        formErrors.value = false
      }
    }
  )
  watch(
    () => user.value.email,
    async () => {
      updateUserForm(user.value)
    }
  )

  onMounted(() => {
    if (props.user) {
      store.dispatch(AUTH_USER_STORE.ACTIONS.GET_REQUEST_DATA_EXPORT)
      updateUserForm(props.user)
    }
  })
  onUnmounted(() => {
    store.commit(AUTH_USER_STORE.MUTATIONS.UPDATE_IS_SUCCESS, false)
  })
</script>

<style lang="scss" scoped>
  @use '~@/scss/vars.scss' as *;
  #user-account-edition {
    padding: $default-padding 0;

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
      display: flex;
      flex-direction: row;
      gap: $default-padding;
      margin-top: $default-margin;
      @media screen and (max-width: $x-small-limit) {
        flex-direction: column;
      }
    }
  }
</style>
