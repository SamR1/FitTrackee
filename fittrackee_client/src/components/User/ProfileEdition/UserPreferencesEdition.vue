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
        <label class="form-items">
          {{ $t('user.PROFILE.TIMEZONE') }}
          <TimezoneDropdown
            :input="userForm.timezone"
            :disabled="loading"
            @updateTimezone="updateTZ"
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
        <label class="form-items">
          {{ $t('user.PROFILE.UNITS.LABEL') }}
          <select
            id="imperial_units"
            v-model="userForm.imperial_units"
            :disabled="loading"
          >
            <option
              v-for="unit in imperialUnits"
              :value="unit.value"
              :key="unit.value"
            >
              {{ $t(`user.PROFILE.UNITS.${unit.label}`) }}
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

<script setup lang="ts">
  import { ComputedRef, computed, reactive, onMounted, onUnmounted } from 'vue'

  import TimezoneDropdown from '@/components/User/ProfileEdition/TimezoneDropdown.vue'
  import { AUTH_USER_STORE, ROOT_STORE } from '@/store/constants'
  import { IUserProfile, IUserPreferencesPayload } from '@/types/user'
  import { useStore } from '@/use/useStore'
  import { availableLanguages } from '@/utils/locales'

  interface Props {
    user: IUserProfile
  }
  const props = defineProps<Props>()

  const store = useStore()

  const userForm: IUserPreferencesPayload = reactive({
    imperial_units: false,
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
  const imperialUnits = [
    {
      label: 'IMPERIAL',
      value: true,
    },
    {
      label: 'METRIC',
      value: false,
    },
  ]
  const loading = computed(
    () => store.getters[AUTH_USER_STORE.GETTERS.USER_LOADING]
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
    userForm.imperial_units = user.imperial_units ? user.imperial_units : false
    userForm.language = user.language ? user.language : 'en'
    userForm.timezone = user.timezone ? user.timezone : 'Europe/Paris'
    userForm.weekm = user.weekm ? user.weekm : false
  }
  function updateProfile() {
    store.dispatch(AUTH_USER_STORE.ACTIONS.UPDATE_USER_PREFERENCES, userForm)
  }
  function updateTZ(value: string) {
    userForm.timezone = value
  }

  onUnmounted(() => {
    store.commit(ROOT_STORE.MUTATIONS.EMPTY_ERROR_MESSAGES)
  })
</script>
