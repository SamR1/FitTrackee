<template>
  <div id="user-infos-edition">
    <div class="profile-form form-box">
      <ErrorMessage :message="errorMessages" v-if="errorMessages" />
      <form @submit.prevent="updateProfile">
        <label class="form-items" for="registrationDate">
          {{ $t('user.PROFILE.REGISTRATION_DATE') }}
          <input id="registrationDate" :value="registrationDate" disabled />
        </label>
        <label class="form-items" for="first_name">
          {{ $t('user.PROFILE.FIRST_NAME') }}
          <input
            id="first_name"
            v-model="userForm.first_name"
            :disabled="authUserLoading"
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
            :disabled="authUserLoading"
          />
        </label>
        <label class="form-items" for="location">
          {{ $t('user.PROFILE.LOCATION') }}
          <input
            id="location"
            v-model="userForm.location"
            :disabled="authUserLoading"
          />
        </label>
        <label class="form-items">
          {{ $t('user.PROFILE.BIO') }}
          <CustomTextArea
            name="bio"
            :charLimit="200"
            :input="userForm.bio"
            :disabled="authUserLoading"
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
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
  import { format } from 'date-fns'
  import { computed, reactive, onMounted, toRefs } from 'vue'
  import type { ComputedRef, Reactive } from 'vue'

  import useApp from '@/composables/useApp'
  import useAuthUser from '@/composables/useAuthUser'
  import { AUTH_USER_STORE } from '@/store/constants'
  import type { ICustomTextareaData } from '@/types/forms'
  import type {
    IUserProfile,
    IUserPayload,
    IAuthUserProfile,
  } from '@/types/user'
  import { useStore } from '@/use/useStore'
  import { formatDate } from '@/utils/dates'

  interface Props {
    user: IAuthUserProfile
  }
  const props = defineProps<Props>()
  const { user } = toRefs(props)

  const store = useStore()

  const { errorMessages } = useApp()
  const { authUserLoading } = useAuthUser()

  const userForm: Reactive<IUserPayload> = reactive({
    first_name: '',
    last_name: '',
    birth_date: '',
    location: '',
    bio: '',
  })

  const registrationDate: ComputedRef<string> = computed(() =>
    user.value.created_at
      ? formatDate(
          user.value.created_at,
          user.value.timezone,
          user.value.date_format
        )
      : ''
  )

  function updateUserForm(user: IUserProfile) {
    userForm.first_name = user.first_name ? user.first_name : ''
    userForm.last_name = user.last_name ? user.last_name : ''
    userForm.birth_date = user.birth_date
      ? format(new Date(user.birth_date), 'yyyy-MM-dd')
      : ''
    userForm.location = user.location ? user.location : ''
    userForm.bio = user.bio ? user.bio : ''
  }
  function updateBio(textareaData: ICustomTextareaData) {
    userForm.bio = textareaData.value
  }
  function updateProfile() {
    store.dispatch(AUTH_USER_STORE.ACTIONS.UPDATE_USER_PROFILE, userForm)
  }

  onMounted(() => {
    if (user.value) {
      updateUserForm(user.value)
    }
  })
</script>

<style lang="scss" scoped>
  @import '~@/scss/vars.scss';
  #user-infos-edition {
    padding-top: $default-padding;
    .form-items {
      .password-input {
        ::v-deep(.show-password) {
          font-weight: normal;
          font-size: 0.8em;
          margin-top: -4px;
          padding-left: 0;
        }
      }
    }

    .form-buttons {
      flex-direction: row;
      @media screen and (max-width: $x-small-limit) {
        flex-direction: column;
      }
    }
  }
</style>
