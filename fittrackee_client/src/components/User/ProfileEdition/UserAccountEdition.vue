<template>
  <div id="user-infos-edition">
    <Modal
      v-if="displayModal"
      :title="$t('common.CONFIRMATION')"
      :message="$t('user.CONFIRM_ACCOUNT_DELETION')"
      @confirmAction="deleteAccount(user.username)"
      @cancelAction="updateDisplayModal(false)"
      @keydown.esc="updateDisplayModal(false)"
    />
    <div class="profile-form form-box">
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
          <button class="cancel" @click.prevent="$router.push('/profile')">
            {{ $t('buttons.CANCEL') }}
          </button>
          <button class="danger" @click.prevent="updateDisplayModal(true)">
            {{ $t('buttons.DELETE_MY_ACCOUNT') }}
          </button>
          <button
            class="confirm"
            v-if="canRequestExport()"
            @click.prevent="requestExport"
          >
            {{ $t('buttons.REQUEST_DATA_EXPORT') }}
          </button>
        </div>
      </form>
      <div class="data-export">
        <span class="info-box">
          <i class="fa fa-info-circle" aria-hidden="true" />
          {{ $t('user.EXPORT_REQUEST.ONLY_ONE_EXPORT_PER_DAY') }}
        </span>
        <div v-if="exportRequest" class="data-export-archive">
          {{ $t('user.EXPORT_REQUEST.DATA_EXPORT') }}
          ({{ exportRequestDate }}):
          <span
            v-if="exportRequest.status === 'successful'"
            class="archive-link"
            @click.prevent="downloadArchive(exportRequest.file_name)"
          >
            <i class="fa fa-download" aria-hidden="true" />
            {{ $t('user.EXPORT_REQUEST.DOWNLOAD_ARCHIVE') }}
            ({{ getReadableFileSizeAsText(exportRequest.file_size) }})
          </span>
          <span v-else>
            {{ $t(`user.EXPORT_REQUEST.STATUS.${exportRequest.status}`) }}
          </span>
          <span v-if="generatingLink">
            {{ $t(`user.EXPORT_REQUEST.GENERATING_LINK`) }}
            <i class="fa fa-spinner fa-pulse" aria-hidden="true" />
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
  import { isBefore, subDays } from 'date-fns'
  import {
    computed,
    reactive,
    ref,
    toRefs,
    onMounted,
    watch,
    onUnmounted,
  } from 'vue'
  import type { ComputedRef, Reactive, Ref } from 'vue'

  import authApi from '@/api/authApi'
  import PasswordInput from '@/components/Common/PasswordInput.vue'
  import useApp from '@/composables/useApp'
  import useAuthUser from '@/composables/useAuthUser'
  import { AUTH_USER_STORE } from '@/store/constants'
  import type {
    IAuthUserProfile,
    IUserAccountPayload,
    IExportRequest,
  } from '@/types/user'
  import { useStore } from '@/use/useStore'
  import { formatDate } from '@/utils/dates'
  import { getReadableFileSizeAsText } from '@/utils/files'

  interface Props {
    user: IAuthUserProfile
  }
  const props = defineProps<Props>()
  const { user } = toRefs(props)

  const store = useStore()

  const { appConfig, errorMessages } = useApp()
  const { authUserLoading, authUserSuccess } = useAuthUser()

  const userForm: Reactive<IUserAccountPayload> = reactive({
    email: '',
    password: '',
    new_password: '',
  })
  const emailUpdate: Ref<boolean> = ref(false)
  const formErrors: Ref<boolean> = ref(false)
  const displayModal: Ref<boolean> = ref(false)
  const generatingLink: Ref<boolean> = ref(false)

  const exportRequest: ComputedRef<IExportRequest | null> = computed(
    () => store.getters[AUTH_USER_STORE.GETTERS.EXPORT_REQUEST]
  )
  const exportRequestDate: ComputedRef<string | null> = computed(() =>
    getExportRequestDate()
  )

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
  function getExportRequestDate() {
    return exportRequest.value
      ? formatDate(
          exportRequest.value.created_at,
          user.value.timezone,
          user.value.date_format,
          true,
          null,
          true
        )
      : null
  }
  function canRequestExport() {
    return exportRequestDate.value
      ? isBefore(new Date(exportRequestDate.value), subDays(new Date(), 1))
      : true
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
  function requestExport() {
    store.dispatch(AUTH_USER_STORE.ACTIONS.REQUEST_DATA_EXPORT)
  }
  async function downloadArchive(filename: string) {
    generatingLink.value = true
    await authApi
      .get(`/auth/account/export/${filename}`, {
        responseType: 'blob',
      })
      .then((response) => {
        const archiveFileUrl = window.URL.createObjectURL(
          new Blob([response.data], { type: 'application/zip' })
        )
        const archive_link = document.createElement('a')
        archive_link.href = archiveFileUrl
        archive_link.setAttribute('download', filename)
        document.body.appendChild(archive_link)
        archive_link.click()
      })
      .finally(() => (generatingLink.value = false))
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
  @import '~@/scss/vars.scss';
  #user-infos-edition {
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
      flex-direction: row;
      @media screen and (max-width: $x-small-limit) {
        flex-direction: column;
      }
    }

    .data-export {
      padding: $default-padding 0;
      .data-export-archive {
        padding-top: $default-padding * 2;
        font-size: 0.9em;

        .archive-link {
          color: var(--app-a-color);
          cursor: pointer;
        }
      }
    }
  }
</style>
