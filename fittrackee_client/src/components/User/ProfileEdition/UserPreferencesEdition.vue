<template>
  <div id="user-preferences-edition">
    <div class="profile-form form-box">
      <ErrorMessage :message="errorMessages" v-if="errorMessages" />
      <form @submit.prevent="updateProfile">
        <div class="preferences-section">
          {{ $t('user.PROFILE.INTERFACE') }}
        </div>
        <label class="form-items">
          {{ $t('user.PROFILE.LANGUAGE') }}
          <select
            id="language"
            v-model="userForm.language"
            :disabled="authUserLoading"
          >
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
          {{ $t('user.PROFILE.THEME_MODE.LABEL') }}
          <select
            id="use_dark_mode"
            v-model="userForm.use_dark_mode"
            :disabled="authUserLoading"
          >
            <option
              v-for="mode in useDarkMode"
              :value="mode.value"
              :key="mode.label"
            >
              {{ $t(`user.PROFILE.THEME_MODE.VALUES.${mode.label}`) }}
            </option>
          </select>
        </label>
        <label class="form-items">
          {{ $t('user.PROFILE.TIMEZONE') }}
          <TimezoneDropdown
            :input="userForm.timezone"
            :disabled="authUserLoading"
            @updateTimezone="(e) => updateValue('timezone', e)"
          />
        </label>
        <label class="form-items">
          {{ $t('user.PROFILE.DATE_FORMAT') }}
          <select
            id="date_format"
            v-model="userForm.date_format"
            :disabled="authUserLoading"
          >
            <option
              v-for="dateFormat in dateFormatOptions"
              :value="dateFormat.value"
              :key="dateFormat.value"
            >
              {{ dateFormat.label }}
            </option>
          </select>
        </label>
        <div class="form-items form-checkboxes">
          <span class="checkboxes-label">
            {{ $t('user.PROFILE.FIRST_DAY_OF_WEEK') }}
          </span>
          <div class="checkboxes">
            <label v-for="start in weekStart" :key="start.label">
              <input
                type="radio"
                :id="start.label"
                :name="start.label"
                :checked="start.value === userForm.weekm"
                :disabled="authUserLoading"
                @input="updateValue('weekm', start.value)"
              />
              <span class="checkbox-label">
                {{ $t(`user.PROFILE.${start.label}`) }}
              </span>
            </label>
          </div>
        </div>
        <div class="preferences-section">
          {{ $t('user.PROFILE.TABS.ACCOUNT') }}
        </div>
        <div class="form-items form-checkboxes">
          <span class="checkboxes-label">
            {{ $t('user.PROFILE.FOLLOW_REQUESTS_APPROVAL.LABEL') }}
          </span>
          <div class="checkboxes">
            <label
              v-for="status in manuallyApprovesFollowersValues"
              :key="status.label"
            >
              <input
                type="radio"
                :id="status.label"
                :name="status.label"
                :checked="status.value === userForm.manually_approves_followers"
                :disabled="authUserLoading"
                @input="
                  updateValue('manually_approves_followers', status.value)
                "
              />
              <span class="checkbox-label">
                {{
                  $t(`user.PROFILE.FOLLOW_REQUESTS_APPROVAL.${status.label}`)
                }}
              </span>
            </label>
          </div>
        </div>
        <div class="form-items form-checkboxes">
          <span class="checkboxes-label">
            {{ $t('user.PROFILE.PROFILE_IN_USERS_DIRECTORY.LABEL') }}
          </span>
          <div class="checkboxes">
            <label
              v-for="status in profileInUsersDirectory"
              :key="status.label"
            >
              <input
                type="radio"
                :id="`hide_profile_${status.label}`"
                :name="`hide_profile_${status.label}`"
                :checked="
                  status.value === userForm.hide_profile_in_users_directory
                "
                :disabled="authUserLoading"
                @input="
                  updateValue('hide_profile_in_users_directory', status.value)
                "
              />
              <span class="checkbox-label">
                {{
                  $t(`user.PROFILE.PROFILE_IN_USERS_DIRECTORY.${status.label}`)
                }}
              </span>
            </label>
          </div>
        </div>
        <div class="preferences-section">{{ $t('workouts.WORKOUT', 0) }}</div>
        <div class="form-items form-checkboxes">
          <span class="checkboxes-label">
            {{ $t('user.PROFILE.UNITS.LABEL') }}
          </span>
          <div class="checkboxes">
            <label v-for="unit in imperialUnits" :key="unit.label">
              <input
                type="radio"
                :id="unit.label"
                :name="unit.label"
                :checked="unit.value === userForm.imperial_units"
                :disabled="authUserLoading"
                @input="updateValue('imperial_units', unit.value)"
              />
              <span class="checkbox-label">
                {{ $t(`user.PROFILE.UNITS.${unit.label}`) }}
              </span>
            </label>
          </div>
        </div>
        <div class="form-items form-checkboxes">
          <span class="checkboxes-label">
            {{ $t('user.PROFILE.ASCENT_DATA') }}
          </span>
          <div class="checkboxes">
            <label v-for="status in ascentData" :key="status.label">
              <input
                type="radio"
                :id="status.label"
                :name="status.label"
                :checked="status.value === userForm.display_ascent"
                :disabled="authUserLoading"
                @input="updateValue('display_ascent', status.value)"
              />
              <span class="checkbox-label">
                {{ $t(`common.${status.label}`) }}
              </span>
            </label>
          </div>
        </div>
        <div class="form-items form-checkboxes">
          <span class="checkboxes-label">
            {{ $t('user.PROFILE.ELEVATION_CHART_START.LABEL') }}
          </span>
          <div class="checkboxes">
            <label
              v-for="status in startElevationAtZeroData"
              :key="status.label"
            >
              <input
                type="radio"
                :id="status.label"
                :name="status.label"
                :checked="status.value === userForm.start_elevation_at_zero"
                :disabled="authUserLoading"
                @input="updateValue('start_elevation_at_zero', status.value)"
              />
              <span class="checkbox-label">
                {{ $t(`user.PROFILE.ELEVATION_CHART_START.${status.label}`) }}
              </span>
            </label>
          </div>
        </div>
        <div class="form-items form-checkboxes">
          <span class="checkboxes-label">
            {{ $t('user.PROFILE.USE_RAW_GPX_SPEED.LABEL') }}
          </span>
          <div class="checkboxes">
            <label v-for="status in useRawGpxSpeed" :key="status.label">
              <input
                type="radio"
                :id="status.label"
                :name="status.label"
                :checked="status.value === userForm.use_raw_gpx_speed"
                :disabled="authUserLoading"
                @input="updateValue('use_raw_gpx_speed', status.value)"
              />
              <span class="checkbox-label">
                {{ $t(`user.PROFILE.USE_RAW_GPX_SPEED.${status.label}`) }}
              </span>
            </label>
          </div>
          <div class="info-box raw-speed-help">
            <span>
              <i class="fa fa-info-circle" aria-hidden="true" />
              {{ $t('user.PROFILE.USE_RAW_GPX_SPEED.HELP') }}
            </span>
          </div>
        </div>
        <label class="form-items">
          {{ $t('visibility_levels.WORKOUTS_VISIBILITY') }}
          <select
            id="workouts_visibility"
            v-model="userForm.workouts_visibility"
            :disabled="authUserLoading"
            @change="updateAnalysisAndMapVisibility"
          >
            <option
              v-for="level in visibilityLevels"
              :value="level"
              :key="level"
            >
              {{ $t(`visibility_levels.LEVELS.${level}`) }}
            </option>
          </select>
        </label>
        <label class="form-items">
          {{ $t('visibility_levels.ANALYSIS_VISIBILITY') }}
          <select
            id="analysis_visibility"
            v-model="userForm.analysis_visibility"
            :disabled="authUserLoading"
            @change="updateMapVisibility"
          >
            <option
              v-for="level in analysisVisibilityLevels"
              :value="level"
              :key="level"
            >
              {{ $t(`visibility_levels.LEVELS.${level}`) }}
            </option>
          </select>
        </label>
        <label class="form-items">
          {{ $t('visibility_levels.MAP_VISIBILITY') }}
          <select
            id="map_visibility"
            v-model="userForm.map_visibility"
            :disabled="authUserLoading"
          >
            <option
              v-for="level in mapVisibilityLevels"
              :value="level"
              :key="level"
            >
              {{ $t(`visibility_levels.LEVELS.${level}`) }}
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
  import { computed, reactive, onMounted, toRefs } from 'vue'
  import type { ComputedRef, Reactive } from 'vue'

  import TimezoneDropdown from '@/components/User/ProfileEdition/TimezoneDropdown.vue'
  import useApp from '@/composables/useApp'
  import useAuthUser from '@/composables/useAuthUser'
  import { AUTH_USER_STORE } from '@/store/constants'
  import type {
    IUserPreferencesPayload,
    IAuthUserProfile,
    TVisibilityLevels,
  } from '@/types/user'
  import { useStore } from '@/use/useStore'
  import { availableDateFormatOptions } from '@/utils/dates'
  import { availableLanguages, languageLabels } from '@/utils/locales'
  import {
    visibilityLevels,
    getVisibilityLevels,
    getUpdatedVisibility,
  } from '@/utils/visibility_levels'

  interface Props {
    user: IAuthUserProfile
  }
  const props = defineProps<Props>()
  const { user } = toRefs(props)

  const store = useStore()

  const { errorMessages } = useApp()
  const { authUserLoading } = useAuthUser()

  const weekStart = [
    {
      label: 'SUNDAY',
      value: false,
    },
    {
      label: 'MONDAY',
      value: true,
    },
  ]
  const imperialUnits = [
    {
      label: 'METRIC',
      value: false,
    },
    {
      label: 'IMPERIAL',
      value: true,
    },
  ]
  const ascentData = [
    {
      label: 'DISPLAYED',
      value: true,
    },
    {
      label: 'HIDDEN',
      value: false,
    },
  ]
  const startElevationAtZeroData = [
    {
      label: 'ZERO',
      value: true,
    },
    {
      label: 'MIN_ALT',
      value: false,
    },
  ]
  const useRawGpxSpeed = [
    {
      label: 'FILTERED_SPEED',
      value: false,
    },
    {
      label: 'RAW_SPEED',
      value: true,
    },
  ]
  const useDarkMode = [
    {
      label: 'DARK',
      value: true,
    },
    {
      label: 'DEFAULT',
      value: null,
    },
    {
      label: 'LIGHT',
      value: false,
    },
  ]
  const manuallyApprovesFollowersValues = [
    {
      label: 'MANUALLY',
      value: true,
    },
    {
      label: 'AUTOMATICALLY',
      value: false,
    },
  ]
  const profileInUsersDirectory = [
    {
      label: 'HIDDEN',
      value: true,
    },
    {
      label: 'DISPLAYED',
      value: false,
    },
  ]

  const userForm: Reactive<IUserPreferencesPayload> = reactive({
    analysis_visibility: 'private',
    date_format: 'dd/MM/yyyy',
    display_ascent: true,
    hide_profile_in_users_directory: true,
    imperial_units: false,
    language: 'en',
    manually_approves_followers: true,
    map_visibility: 'private',
    start_elevation_at_zero: false,
    timezone: 'Europe/Paris',
    use_dark_mode: false,
    use_raw_gpx_speed: false,
    weekm: false,
    workouts_visibility: 'private',
  })

  const dateFormatOptions: ComputedRef<Record<string, string>[]> = computed(
    () =>
      availableDateFormatOptions(
        new Date().toUTCString(),
        user.value.timezone,
        userForm.language
      )
  )

  const analysisVisibilityLevels: ComputedRef<TVisibilityLevels[]> = computed(
    () => getVisibilityLevels(userForm.workouts_visibility)
  )
  const mapVisibilityLevels: ComputedRef<TVisibilityLevels[]> = computed(() =>
    getVisibilityLevels(userForm.analysis_visibility)
  )

  function updateUserForm(user: IAuthUserProfile) {
    userForm.analysis_visibility = user.analysis_visibility
      ? user.analysis_visibility
      : 'private'
    userForm.display_ascent = user.display_ascent
    userForm.start_elevation_at_zero = user.start_elevation_at_zero
      ? user.start_elevation_at_zero
      : false
    userForm.use_raw_gpx_speed = user.use_raw_gpx_speed
      ? user.use_raw_gpx_speed
      : false
    userForm.imperial_units = user.imperial_units ? user.imperial_units : false
    userForm.language =
      user.language && user.language in languageLabels ? user.language : 'en'
    userForm.manually_approves_followers =
      'manually_approves_followers' in user
        ? user.manually_approves_followers
        : true
    userForm.map_visibility = user.map_visibility
      ? user.map_visibility
      : 'private'
    userForm.timezone = user.timezone ? user.timezone : 'Europe/Paris'
    userForm.date_format = user.date_format ? user.date_format : 'dd/MM/yyyy'
    userForm.weekm = user.weekm ? user.weekm : false
    userForm.use_dark_mode = user.use_dark_mode
    userForm.workouts_visibility = user.workouts_visibility
      ? user.workouts_visibility
      : 'private'
    userForm.hide_profile_in_users_directory =
      user.hide_profile_in_users_directory
  }
  function updateProfile() {
    store.dispatch(AUTH_USER_STORE.ACTIONS.UPDATE_USER_PREFERENCES, userForm)
  }
  function updateValue(key: string, value: string | boolean) {
    // eslint-disable-next-line @typescript-eslint/ban-ts-comment
    // @ts-ignore
    userForm[key] = value
  }
  function updateAnalysisAndMapVisibility() {
    userForm.analysis_visibility = getUpdatedVisibility(
      userForm.analysis_visibility,
      userForm.workouts_visibility
    )
    updateMapVisibility()
  }
  function updateMapVisibility() {
    userForm.map_visibility = getUpdatedVisibility(
      userForm.map_visibility,
      userForm.analysis_visibility
    )
  }

  onMounted(() => {
    if (user.value) {
      updateUserForm(user.value)
    }
  })
</script>

<style lang="scss" scoped>
  @import '~@/scss/vars.scss';
  #user-preferences-edition {
    padding-top: $default-padding;
    .form-items {
      padding-top: $default-padding * 0.5;
    }

    .form-checkboxes {
      .checkboxes-label {
        font-weight: bold;
      }
      .checkboxes {
        display: flex;
        gap: $default-padding;
        flex-wrap: wrap;
        .checkbox-label {
          padding-left: $default-padding * 0.5;
        }
        label {
          font-weight: normal;
        }
      }
    }

    .preferences-section {
      font-weight: bold;
      text-transform: uppercase;
      border-bottom: 1px solid var(--card-border-color);
      margin-bottom: $default-padding * 0.5;
    }
    .preferences-section:not(:first-child) {
      margin-top: $default-padding * 1.5;
    }

    #language,
    #date_format,
    #use_dark_mode,
    #map_visibility,
    #analysis_visibility,
    #workouts_visibility {
      padding: $default-padding * 0.5;
    }
  }
</style>
