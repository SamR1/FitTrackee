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
      @keydown.esc="updateDisplayModal('')"
    />
    <div class="info-box success-message" v-if="usersSuccess">
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
      v-if="authUser?.admin && !user.is_remote && !user.is_active"
    />
    <ErrorMessage
      :message="errorMessages"
      v-if="errorMessages && !currentUserReporting"
    />
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
        <dd>
          <time>{{ registrationDate }}</time>
        </dd>
        <dt v-if="user.first_name">{{ $t('user.PROFILE.FIRST_NAME') }}:</dt>
        <dd v-if="user.first_name">{{ user.first_name }}</dd>
        <dt v-if="user.last_name">{{ $t('user.PROFILE.LAST_NAME') }}:</dt>
        <dd v-if="user.last_name">{{ user.last_name }}</dd>
        <dt v-if="birthDate">{{ $t('user.PROFILE.BIRTH_DATE') }}:</dt>
        <dd v-if="birthDate">
          <time>{{ birthDate }}</time>
        </dd>
        <dt v-if="user.location">{{ $t('user.PROFILE.LOCATION') }}:</dt>
        <dd v-if="user.location">{{ user.location }}</dd>
        <dt v-if="user.bio">{{ $t('user.PROFILE.BIO') }}:</dt>
        <dd v-if="user.bio" class="user-bio">
          {{ user.bio }}
        </dd>
      </dl>
      <div
        class="report-submitted"
        v-if="reportStatus === `user-${user.username}-created`"
      >
        <div class="info-box">
          <span>
            <i class="fa fa-info-circle" aria-hidden="true" />
            {{ $t('common.REPORT_SUBMITTED') }}
          </span>
        </div>
      </div>
      <ReportForm
        v-if="currentUserReporting"
        :object-id="user.username"
        object-type="user"
      />
      <template v-else>
        <div class="profile-buttons" v-if="fromAdmin">
          <button
            class="danger"
            v-if="!isAuthUser(user, authUser)"
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
            v-if="authUser?.username !== user.username"
            @click.prevent="displayEmailForm"
          >
            {{ $t('admin.UPDATE_USER_EMAIL') }}
          </button>
          <button
            v-if="
              !isAuthUser(user, authUser) && appConfig.is_email_sending_enabled
            "
            @click.prevent="updateDisplayModal('reset')"
          >
            {{ $t('admin.RESET_USER_PASSWORD') }}
          </button>
          <UserRelationshipActions
            v-if="authUser?.username"
            :authUser="authUser"
            :user="user"
            from="userInfos"
          />
          <button @click="$router.go(-1)">{{ $t('buttons.BACK') }}</button>
        </div>
        <div class="profile-buttons" v-else>
          <button
            v-if="$route.path === '/profile' || isAuthUser(user, authUser)"
            @click="$router.push('/profile/edit')"
          >
            {{ $t('user.PROFILE.EDIT') }}
          </button>
          <UserRelationshipActions
            v-if="authUser?.username"
            :authUser="authUser"
            :user="user"
            from="userInfos"
          />
          <button
            v-if="
              $route.name === 'User' &&
              !isAuthUser(user, authUser) &&
              user.suspended_at === null &&
              reportStatus !== `user-${user.username}-created`
            "
            @click="displayReportForm"
          >
            {{ $t('user.REPORT') }}
          </button>
          <button @click="$router.go(-1)">{{ $t('buttons.BACK') }}</button>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
  import { format } from 'date-fns'
  import { computed, ref, toRefs, watch, onUnmounted } from 'vue'
  import type { ComputedRef, Ref } from 'vue'

  import ReportForm from '@/components/Common/ReportForm.vue'
  import UserRelationshipActions from '@/components/User/UserRelationshipActions.vue'
  import useApp from '@/composables/useApp'
  import { REPORTS_STORE, ROOT_STORE, USERS_STORE } from '@/store/constants'
  import type { IAuthUserProfile, IUserProfile } from '@/types/user'
  import { useStore } from '@/use/useStore'
  import { formatDate, getDateFormat } from '@/utils/dates'
  import { localeFromLanguage } from '@/utils/locales'
  import { isAuthUser } from '@/utils/user'

  interface Props {
    user: IUserProfile
    authUser?: IAuthUserProfile
    fromAdmin?: boolean
  }
  const props = withDefaults(defineProps<Props>(), {
    fromAdmin: false,
  })
  const { authUser, user, fromAdmin } = toRefs(props)

  const store = useStore()

  const { appConfig, appLanguage, displayOptions, errorMessages } = useApp()

  const displayModal: Ref<string> = ref('')
  const formErrors: Ref<boolean> = ref(false)
  const displayUserEmailForm: Ref<boolean> = ref(false)
  const newUserEmail: Ref<string> = ref('')
  const currentAction: Ref<string> = ref('')

  const currentUserReporting: ComputedRef<boolean> = computed(
    () => store.getters[USERS_STORE.GETTERS.USER_CURRENT_REPORTING]
  )
  const reportStatus: ComputedRef<string | null> = computed(
    () => store.getters[REPORTS_STORE.GETTERS.REPORT_STATUS]
  )
  const registrationDate: ComputedRef<string> = computed(() =>
    user.value.created_at
      ? formatDate(
          user.value.created_at,
          displayOptions.value.timezone,
          displayOptions.value.dateFormat
        )
      : ''
  )
  const birthDate: ComputedRef<string> = computed(() =>
    user.value.birth_date
      ? format(
          new Date(user.value.birth_date),
          `${getDateFormat(displayOptions.value.dateFormat, appLanguage.value)}`,
          { locale: localeFromLanguage[appLanguage.value] }
        )
      : ''
  )
  const usersSuccess = computed(
    () => store.getters[USERS_STORE.GETTERS.USERS_IS_SUCCESS]
  )

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
    store.commit(USERS_STORE.MUTATIONS.UPDATE_USER_CURRENT_REPORTING, false)
    store.commit(REPORTS_STORE.MUTATIONS.SET_REPORT_STATUS, null)
    currentAction.value = ''
  }
  function displayReportForm() {
    store.commit(USERS_STORE.MUTATIONS.UPDATE_USER_CURRENT_REPORTING, true)
  }

  watch(
    () => usersSuccess.value,
    (newIsSuccess) => {
      if (newIsSuccess) {
        updateDisplayModal('')
        hideEmailForm()
      }
    }
  )

  onUnmounted(() => resetErrorsAndSuccess())
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
      ::v-deep(.actions-buttons) {
        gap: $default-padding;
      }
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
    .report-submitted {
      display: flex;
      .info-box {
        margin-bottom: $default-margin;
      }
    }
    .suspended {
      margin-top: $default-margin;
    }

    .remote-user-account {
      margin: $default-margin * 2 0;
      a {
        text-decoration: underline;
      }
    }
  }
</style>
