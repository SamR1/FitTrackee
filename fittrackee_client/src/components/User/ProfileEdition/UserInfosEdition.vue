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
      <form @submit.prevent="updateProfile">
        <label class="form-items" for="email">
          {{ $t('user.EMAIL') }}
          <input id="email" :value="user.email" disabled />
        </label>
        <label class="form-items" for="registrationDate">
          {{ $t('user.PROFILE.REGISTRATION_DATE') }}
          <input id="registrationDate" :value="registrationDate" disabled />
        </label>
        <label class="form-items" for="password">
          {{ $t('user.PASSWORD') }}
          <input
            id="password"
            type="password"
            v-model="userForm.password"
            :disabled="loading"
          />
        </label>
        <hr />
        <label class="form-items" for="first_name">
          {{ $t('user.PROFILE.FIRST_NAME') }}
          <input
            id="first_name"
            v-model="userForm.first_name"
            :disabled="loading"
          />
        </label>
        <label class="form-items" for="last_name">
          {{ $t('user.PROFILE.LAST_NAME') }}
          <input id="last_name" v-model="userForm.last_name" />
        </label>
        <label class="form-items" for="birth_date">
          {{ $t('user.PROFILE.BIRTH_DATE') }}
          <input
            id="birth_date"
            type="date"
            class="birth-date"
            v-model="userForm.birth_date"
            :disabled="loading"
          />
        </label>
        <label class="form-items" for="location">
          {{ $t('user.PROFILE.LOCATION') }}
          <input
            id="location"
            v-model="userForm.location"
            :disabled="loading"
          />
        </label>
        <label class="form-items">
          {{ $t('user.PROFILE.BIO') }}
          <CustomTextArea
            name="bio"
            :charLimit="200"
            :input="userForm.bio"
            :disabled="loading"
            @updateValue="updateBio"
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
  import { format } from 'date-fns'
  import {
    ComputedRef,
    Ref,
    computed,
    reactive,
    ref,
    toRefs,
    onMounted,
  } from 'vue'

  import { AUTH_USER_STORE, ROOT_STORE } from '@/store/constants'
  import { IUserProfile, IUserPayload } from '@/types/user'
  import { useStore } from '@/use/useStore'

  interface Props {
    user: IUserProfile
  }
  const props = defineProps<Props>()

  const store = useStore()

  const { user } = toRefs(props)
  const userForm: IUserPayload = reactive({
    password: '',
    first_name: '',
    last_name: '',
    birth_date: '',
    location: '',
    bio: '',
  })
  const registrationDate = computed(() =>
    props.user.created_at
      ? format(new Date(props.user.created_at), 'dd/MM/yyyy HH:mm')
      : ''
  )
  const loading = computed(
    () => store.getters[AUTH_USER_STORE.GETTERS.USER_LOADING]
  )
  const errorMessages: ComputedRef<string | string[] | null> = computed(
    () => store.getters[ROOT_STORE.GETTERS.ERROR_MESSAGES]
  )
  let displayModal: Ref<boolean> = ref(false)

  onMounted(() => {
    if (props.user) {
      updateUserForm(props.user)
    }
  })

  function updateUserForm(user: IUserProfile) {
    userForm.first_name = user.first_name ? user.first_name : ''
    userForm.last_name = user.last_name ? user.last_name : ''
    userForm.birth_date = user.birth_date
      ? format(new Date(user.birth_date), 'yyyy-MM-dd')
      : ''
    userForm.location = user.location ? user.location : ''
    userForm.bio = user.bio ? user.bio : ''
  }
  function updateBio(value: string) {
    userForm.bio = value
  }
  function updateProfile() {
    store.dispatch(AUTH_USER_STORE.ACTIONS.UPDATE_USER_PROFILE, userForm)
  }
  function updateDisplayModal(value: boolean) {
    displayModal.value = value
  }
  function deleteAccount(username: string) {
    store.dispatch(AUTH_USER_STORE.ACTIONS.DELETE_ACCOUNT, { username })
  }
</script>

<style lang="scss">
  @import '~@/scss/vars.scss';

  .form-buttons {
    flex-direction: row;
    @media screen and (max-width: $x-small-limit) {
      flex-direction: column;
    }
  }
</style>
