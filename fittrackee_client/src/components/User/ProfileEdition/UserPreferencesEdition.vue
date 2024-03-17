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
          {{ $t('user.PROFILE.THEME_MODE.LABEL') }}
          <select
            id="use_dark_mode"
            v-model="userForm.use_dark_mode"
            :disabled="loading"
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
            :disabled="loading"
            @updateTimezone="updateTZ"
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
                @input="updateWeekM(start.value)"
              />
              <span class="checkbox-label">
                {{ $t(`user.PROFILE.${start.label}`) }}
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
                :disabled="loading"
                @input="updateImperialUnit(unit.value)"
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
                @input="updateAscentDisplay(status.value)"
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
                @input="updateStartElevationAtZero(status.value)"
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
                @input="updateUseRawGpxSpeed(status.value)"
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
  import { computed, reactive, onMounted, onUnmounted } from 'vue'
  import type { ComputedRef } from 'vue'

  import TimezoneDropdown from '@/components/User/ProfileEdition/TimezoneDropdown.vue'
  import { AUTH_USER_STORE, ROOT_STORE } from '@/store/constants'
  import type { IUserPreferencesPayload, IAuthUserProfile } from '@/types/user'
  import { useStore } from '@/use/useStore'
  import { availableDateFormatOptions } from '@/utils/dates'
  import { availableLanguages } from '@/utils/locales'

  interface Props {
    user: IAuthUserProfile
  }
  const props = defineProps<Props>()

  const store = useStore()

  const userForm: IUserPreferencesPayload = reactive({
    display_ascent: true,
    imperial_units: false,
    language: 'en',
    timezone: 'Europe/Paris',
    date_format: 'dd/MM/yyyy',
    weekm: false,
    start_elevation_at_zero: false,
    use_raw_gpx_speed: false,
    use_dark_mode: false,
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
    userForm.timezone = user.timezone ? user.timezone : 'Europe/Paris'
    userForm.date_format = user.date_format ? user.date_format : 'dd/MM/yyyy'
    userForm.weekm = user.weekm ? user.weekm : false
    userForm.use_dark_mode = user.use_dark_mode
  }
  function updateProfile() {
    store.dispatch(AUTH_USER_STORE.ACTIONS.UPDATE_USER_PREFERENCES, userForm)
  }
  function updateTZ(value: string) {
    userForm.timezone = value
  }
  function updateStartElevationAtZero(value: boolean) {
    userForm.start_elevation_at_zero = value
  }
  function updateUseRawGpxSpeed(value: boolean) {
    userForm.use_raw_gpx_speed = value
  }
  function updateAscentDisplay(value: boolean) {
    userForm.display_ascent = value
  }
  function updateImperialUnit(value: boolean) {
    userForm.imperial_units = value
  }
  function updateWeekM(value: boolean) {
    userForm.weekm = value
  }

  onUnmounted(() => {
    store.commit(ROOT_STORE.MUTATIONS.EMPTY_ERROR_MESSAGES)
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
    #use_dark_mode {
      padding: $default-padding * 0.5;
    }
  }
</style>
