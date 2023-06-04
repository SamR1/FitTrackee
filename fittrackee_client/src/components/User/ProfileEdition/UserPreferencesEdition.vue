<template>
  <div id="user-preferences-edition">
    <div class="profile-form form-box">
      <ErrorMessage :message="errorMessages" v-if="errorMessages" />
      <form @submit.prevent="updateProfile">
        <p class="preferences-section">{{ $t('user.PROFILE.INTERFACE') }}</p>
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
            @updateTimezone="(e) => updateValue('timezone', e)"
          />
        </label>
        <label class="form-items">
          {{ $t('user.PROFILE.DATE_FORMAT') }}
          <select
            id="date_format"
            v-model="userForm.date_format"
            :disabled="loading"
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
                :disabled="loading"
                @input="updateValue('weekm', start.value)"
              />
              <span class="checkbox-label">
                {{ $t(`user.PROFILE.${start.label}`) }}
              </span>
            </label>
          </div>
        </div>
        <p class="preferences-section">{{ $t('user.PROFILE.TABS.ACCOUNT') }}</p>
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
                :disabled="loading"
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
                :disabled="loading"
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
        <p class="preferences-section">{{ $t('workouts.WORKOUT') }}</p>
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
                :disabled="loading"
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
                :disabled="loading"
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
                :disabled="loading"
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
                :disabled="loading"
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
          {{ $t('privacy.WORKOUTS_VISIBILITY') }}
          <select
            id="workouts_visibility"
            v-model="userForm.workouts_visibility"
            :disabled="loading"
            @change="updateMapVisibility"
          >
            <option v-for="level in privacyLevels" :value="level" :key="level">
              {{
                $t(
                  `privacy.LEVELS.${getPrivacyLevelForLabel(
                    level,
                    appConfig.federation_enabled
                  )}`
                )
              }}
            </option>
          </select>
        </label>
        <label class="form-items">
          {{ $t('privacy.MAP_VISIBILITY') }}
          <select
            id="map_visibility"
            v-model="userForm.map_visibility"
            :disabled="loading"
          >
            <option
              v-for="level in mapPrivacyLevels"
              :value="level"
              :key="level"
            >
              {{
                $t(
                  `privacy.LEVELS.${getPrivacyLevelForLabel(
                    level,
                    appConfig.federation_enabled
                  )}`
                )
              }}
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
  import { TAppConfig } from '@/types/application'
  import { IUserPreferencesPayload, IAuthUserProfile } from '@/types/user'
  import { useStore } from '@/use/useStore'
  import { availableDateFormatOptions } from '@/utils/dates'
  import { availableLanguages } from '@/utils/locales'
  import {
    getPrivacyLevels,
    getPrivacyLevelForLabel,
    getMapVisibilityLevels,
    getUpdatedMapVisibility,
  } from '@/utils/privacy'

  interface Props {
    user: IAuthUserProfile
  }
  const props = defineProps<Props>()

  const store = useStore()

  const userForm: IUserPreferencesPayload = reactive({
    date_format: 'dd/MM/yyyy',
    display_ascent: true,
    hide_profile_in_users_directory: true,
    imperial_units: false,
    language: '',
    manually_approves_followers: true,
    map_visibility: 'private',
    start_elevation_at_zero: false,
    timezone: 'Europe/Paris',
    use_raw_gpx_speed: false,
    weekm: false,
    workouts_visibility: 'private',
  })
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
  const appConfig: ComputedRef<TAppConfig> = computed(
    () => store.getters[ROOT_STORE.GETTERS.APP_CONFIG]
  )
  const loading = computed(
    () => store.getters[AUTH_USER_STORE.GETTERS.USER_LOADING]
  )
  const errorMessages: ComputedRef<string | string[] | null> = computed(
    () => store.getters[ROOT_STORE.GETTERS.ERROR_MESSAGES]
  )
  const dateFormatOptions = computed(() =>
    availableDateFormatOptions(
      new Date().toUTCString(),
      props.user.timezone,
      userForm.language
    )
  )
  const privacyLevels = computed(() =>
    getPrivacyLevels(appConfig.value.federation_enabled)
  )
  const mapPrivacyLevels = computed(() =>
    getMapVisibilityLevels(userForm.workouts_visibility)
  )

  onMounted(() => {
    if (props.user) {
      updateUserForm(props.user)
    }
  })

  function updateUserForm(user: IAuthUserProfile) {
    userForm.display_ascent = user.display_ascent
    userForm.start_elevation_at_zero = user.start_elevation_at_zero
      ? user.start_elevation_at_zero
      : false
    userForm.use_raw_gpx_speed = user.use_raw_gpx_speed
      ? user.use_raw_gpx_speed
      : false
    userForm.imperial_units = user.imperial_units ? user.imperial_units : false
    userForm.language = user.language ? user.language : 'en'
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
    userForm[key] = value
  }
  function updateMapVisibility() {
    userForm.map_visibility = getUpdatedMapVisibility(
      userForm.map_visibility,
      userForm.workouts_visibility
    )
  }

  onUnmounted(() => {
    store.commit(ROOT_STORE.MUTATIONS.EMPTY_ERROR_MESSAGES)
  })
</script>

<style lang="scss" scoped>
  @import '~@/scss/vars.scss';
  #user-preferences-edition {
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

    #language,
    #date_format,
    #map_visibility,
    #workouts_visibility {
      padding: $default-padding * 0.5;
    }
  }
</style>
