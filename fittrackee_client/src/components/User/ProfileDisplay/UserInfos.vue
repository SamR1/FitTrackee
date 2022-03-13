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
      {{ $t('admin.PASSWORD_RESET_SUCCESSFUL') }}
    </div>
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
        v-if="authUser.username !== user.username"
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
  import { IAuthUserProfile, IUserProfile } from '@/types/user'
  import { useStore } from '@/use/useStore'

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
      ? format(new Date(props.user.created_at), 'dd/MM/yyyy HH:mm')
      : ''
  )
  const birthDate = computed(() =>
    props.user.birth_date
      ? format(new Date(props.user.birth_date), 'dd/MM/yyyy')
      : ''
  )
  const isSuccess = computed(
    () => store.getters[USERS_STORE.GETTERS.USERS_IS_SUCCESS]
  )
  let displayModal: Ref<string> = ref('')

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
    store.dispatch(USERS_STORE.ACTIONS.UPDATE_USER, {
      username,
      resetPassword: true,
    })
  }

  onUnmounted(() => {
    store.commit(ROOT_STORE.MUTATIONS.EMPTY_ERROR_MESSAGES)
    store.commit(USERS_STORE.MUTATIONS.UPDATE_IS_SUCCESS, false)
  })

  watch(
    () => isSuccess.value,
    (newIsSuccess) => {
      if (newIsSuccess) {
        updateDisplayModal('')
      }
    }
  )
</script>

<style lang="scss" scoped>
  #user-infos {
    .user-bio {
      white-space: pre-wrap;
    }
  }
</style>
