<template>
  <div id="user-preferences-edition">
    <div class="profile-form form-box">
      <ErrorMessage :message="errorMessages" v-if="errorMessages" />
      <form @submit.prevent="updateProfile">
        <label class="form-items">
          {{ $t('user.PROFILE.LANGUAGE') }}
          <select id="language" v-model="userForm.language" :disabled="loading">
            <option
              v-for="lang in availableLanguages"
              :value="lang.value"
              :key="lang.value"
            >
              {{ lang.label }}
            </option>
          </select>
        </label>
        <label class="form-items" for="timezone">
          {{ $t('user.PROFILE.TIMEZONE') }}
          <input
            id="timezone"
            v-model="userForm.timezone"
            :disabled="loading"
          />
        </label>
        <label class="form-items">
          {{ $t('user.PROFILE.FIRST_DAY_OF_WEEK') }}
          <select id="weekm" v-model="userForm.weekm" :disabled="loading">
            <option
              v-for="start in weekStart"
              :value="start.value"
              :key="start.value"
            >
              {{ $t(`user.PROFILE.${start.label}`) }}
            </option>
          </select>
        </label>
        <div class="form-buttons">
          <button class="confirm" type="submit">
            {{ $t('buttons.SUBMIT') }}
          </button>
          <button
            class="cancel"
            @click.prevent="$router.push('/profile/preferences')"
          >
            {{ $t('buttons.CANCEL') }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script lang="ts">
  import {
    ComputedRef,
    PropType,
    computed,
    defineComponent,
    reactive,
    onMounted,
  } from 'vue'

  import { ROOT_STORE, USER_STORE } from '@/store/constants'
  import { IUserProfile, IUserPreferencesPayload } from '@/types/user'
  import { useStore } from '@/use/useStore'
  import { availableLanguages } from '@/utils/locales'

  export default defineComponent({
    name: 'UserPreferencesEdition',
    props: {
      user: {
        type: Object as PropType<IUserProfile>,
        required: true,
      },
    },
    setup(props) {
      const store = useStore()
      const userForm: IUserPreferencesPayload = reactive({
        language: '',
        timezone: 'Europe/Paris',
        weekm: false,
      })
      const weekStart = [
        {
          label: 'MONDAY',
          value: true,
        },
        {
          label: 'SUNDAY',
          value: false,
        },
      ]
      const loading = computed(
        () => store.getters[USER_STORE.GETTERS.USER_LOADING]
      )
      const errorMessages: ComputedRef<string | string[] | null> = computed(
        () => store.getters[ROOT_STORE.GETTERS.ERROR_MESSAGES]
      )

      onMounted(() => {
        if (props.user) {
          updateUserForm(props.user)
        }
      })

      function updateUserForm(user: IUserProfile) {
        userForm.language = user.language ? user.language : 'en'
        userForm.timezone = user.timezone ? user.timezone : 'Europe/Paris'
        userForm.weekm = user.weekm ? user.weekm : false
      }
      function updateProfile() {
        store.dispatch(USER_STORE.ACTIONS.UPDATE_USER_PREFERENCES, userForm)
      }

      return {
        availableLanguages,
        errorMessages,
        loading,
        userForm,
        weekStart,
        updateProfile,
      }
    },
  })
</script>
