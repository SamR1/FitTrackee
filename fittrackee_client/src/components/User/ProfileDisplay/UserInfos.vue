<template>
  <div id="user-infos" class="description-list">
    <Modal
      v-if="displayModal"
      :title="$t('common.CONFIRMATION')"
      :message="
        displayModal === 'delete'
          ? 'admin.CONFIRM_USER_ACCOUNT_DELETION'
          : 'admin.CONFIRM_USER_PASSWORD_RESET'
      "
      :strongMessage="user.username"
      @confirmAction="
        displayModal === 'delete'
          ? deleteUserAccount(user.username)
          : resetUserPassword(user.username)
      "
      @cancelAction="updateDisplayModal('')"
    />
    <div class="info-box success-message" v-if="isSuccess">
      {{
        $t(
          `admin.${
            currentAction === 'password-reset'
              ? 'PASSWORD_RESET'
              : 'USER_EMAIL_UPDATE'
          }_SUCCESSFUL`
        )
      }}
    </div>
    <AlertMessage
      message="user.THIS_USER_ACCOUNT_IS_INACTIVE"
      v-if="!user.is_active"
    />
    <ErrorMessage :message="errorMessages" v-if="errorMessages" />
    <div class="email-form form-box" v-if="displayUserEmailForm">
      <form
        :class="{ errors: formErrors }"
        @submit.prevent="updateUserEmail(user.username)"
      >
        <label class="form-items" for="email">
          {{ $t('admin.CURRENT_EMAIL') }}
          <input id="email" type="email" v-model="user.email" disabled />
        </label>
        <label class="form-items" for="email">
          {{ $t('admin.NEW_EMAIL') }}*
          <input id="new-email" type="email" required v-model="newUserEmail" />
        </label>
        <div class="form-buttons">
          <button class="confirm" type="submit">
            {{ $t('buttons.SUBMIT') }}
          </button>
          <button class="cancel" @click.prevent="hideEmailForm">
            {{ $t('buttons.CANCEL') }}
          </button>
        </div>
      </form>
    </div>
    <div v-else>
      <dl>
        <dt>{{ $t('user.PROFILE.REGISTRATION_DATE') }}:</dt>
        <dd>{{ registrationDate }}</dd>
        <dt>{{ $t('user.PROFILE.FIRST_NAME') }}:</dt>
        <dd>{{ user.first_name }}</dd>
        <dt>{{ $t('user.PROFILE.LAST_NAME') }}:</dt>
        <dd>{{ user.last_name }}</dd>
        <dt>{{ $t('user.PROFILE.BIRTH_DATE') }}:</dt>
        <dd>{{ birthDate }}</dd>
        <dt>{{ $t('user.PROFILE.LOCATION') }}:</dt>
        <dd>{{ user.location }}</dd>
        <dt>{{ $t('user.PROFILE.BIO') }}:</dt>
        <dd class="user-bio">
          {{ user.bio }}
        </dd>
      </dl>
      <div class="profile-buttons" v-if="fromAdmin">
        <button
          class="danger"
          v-if="authUser.username !== user.username"
          @click.prevent="updateDisplayModal('delete')"
        >
          {{ $t('admin.DELETE_USER') }}
        </button>
        <button
          v-if="!user.is_active"
          @click.prevent="confirmUserAccount(user.username)"
        >
          {{ $t('admin.ACTIVATE_USER_ACCOUNT') }}
        </button>
        <button
          v-if="authUser.username !== user.username"
          @click.prevent="displayEmailForm"
        >
          {{ $t('admin.UPDATE_USER_EMAIL') }}
        </button>
        <button
          v-if="
            authUser.username !== user.username &&
            appConfig.is_email_sending_enabled
          "
          @click.prevent="updateDisplayModal('reset')"
        >
          {{ $t('admin.RESET_USER_PASSWORD') }}
        </button>
        <button @click="$router.go(-1)">{{ $t('buttons.BACK') }}</button>
      </div>
      <div class="profile-buttons" v-else>
        <button @click="$router.push('/profile/edit')">
          {{ $t('user.PROFILE.EDIT') }}
        </button>
        <button @click="$router.push('/')">{{ $t('common.HOME') }}</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
  import { format } from 'date-fns'
  import {
    ComputedRef,
    Ref,
    computed,
    ref,
    toRefs,
    withDefaults,
    watch,
    onUnmounted,
  } from 'vue'

  import { AUTH_USER_STORE, ROOT_STORE, USERS_STORE } from '@/store/constants'
  import { TAppConfig } from '@/types/application'
  import { IAuthUserProfile, IUserProfile } from '@/types/user'
  import { useStore } from '@/use/useStore'
  import { formatDate } from '@/utils/dates'

  interface Props {
    user: IUserProfile
    fromAdmin?: boolean
  }
  const props = withDefaults(defineProps<Props>(), {
    fromAdmin: false,
  })

  const store = useStore()

  const { user, fromAdmin } = toRefs(props)
  const authUser: ComputedRef<IAuthUserProfile> = computed(
    () => store.getters[AUTH_USER_STORE.GETTERS.AUTH_USER_PROFILE]
  )
  const registrationDate = computed(() =>
    props.user.created_at
      ? formatDate(
          props.user.created_at,
          authUser.value.timezone,
          authUser.value.date_format
        )
      : ''
  )
  const birthDate = computed(() =>
    props.user.birth_date
      ? format(new Date(props.user.birth_date), authUser.value.date_format)
      : ''
  )
  const isSuccess = computed(
    () => store.getters[USERS_STORE.GETTERS.USERS_IS_SUCCESS]
  )
  const errorMessages: ComputedRef<string | string[] | null> = computed(
    () => store.getters[ROOT_STORE.GETTERS.ERROR_MESSAGES]
  )
  const appConfig: ComputedRef<TAppConfig> = computed(
    () => store.getters[ROOT_STORE.GETTERS.APP_CONFIG]
  )
  const displayModal: Ref<string> = ref('')
  const formErrors = ref(false)
  const displayUserEmailForm: Ref<boolean> = ref(false)
  const newUserEmail: Ref<string> = ref('')
  const currentAction: Ref<string> = ref('')

  function updateDisplayModal(value: string) {
    displayModal.value = value
    if (value !== '') {
      store.commit(USERS_STORE.MUTATIONS.UPDATE_IS_SUCCESS, false)
    }
  }
  function deleteUserAccount(username: string) {
    store.dispatch(USERS_STORE.ACTIONS.DELETE_USER_ACCOUNT, { username })
  }
  function resetUserPassword(username: string) {
    currentAction.value = 'password-reset'
    store.dispatch(USERS_STORE.ACTIONS.UPDATE_USER, {
      username,
      resetPassword: true,
    })
  }
  function confirmUserAccount(username: string) {
    store.dispatch(USERS_STORE.ACTIONS.UPDATE_USER, {
      username,
      activate: true,
    })
  }
  function displayEmailForm() {
    resetErrorsAndSuccess()
    newUserEmail.value = user.value.email_to_confirm
      ? user.value.email_to_confirm
      : ''
    displayUserEmailForm.value = true
    currentAction.value = 'email-update'
  }
  function hideEmailForm() {
    newUserEmail.value = ''
    displayUserEmailForm.value = false
  }
  function updateUserEmail(username: string) {
    store.dispatch(USERS_STORE.ACTIONS.UPDATE_USER, {
      username,
      new_email: newUserEmail.value,
    })
  }
  function resetErrorsAndSuccess() {
    store.commit(ROOT_STORE.MUTATIONS.EMPTY_ERROR_MESSAGES)
    store.commit(USERS_STORE.MUTATIONS.UPDATE_IS_SUCCESS, false)
    currentAction.value = ''
  }

  onUnmounted(() => resetErrorsAndSuccess())

  watch(
    () => isSuccess.value,
    (newIsSuccess) => {
      if (newIsSuccess) {
        updateDisplayModal('')
        hideEmailForm()
      }
    }
  )
</script>

<style lang="scss" scoped>
  @import '~@/scss/vars.scss';
  #user-infos {
    .user-bio {
      white-space: pre-wrap;
    }

    .alert-message {
      margin: 0;
    }

    .profile-buttons {
      display: flex;
      flex-wrap: wrap;
    }

    .email-form {
      display: flex;
      form {
        width: 100%;
      }
      .form-buttons {
        display: flex;
        gap: $default-padding;
        margin-top: $default-margin;
      }
    }
  }
</style>
