<template>
  <div id="user-preferences" class="description-list">
    <div class="preferences-section">{{ $t('user.PROFILE.INTERFACE') }}</div>
    <dl>
      <dt>{{ $t('user.PROFILE.LANGUAGE') }}:</dt>
      <dd>{{ userLanguage }}</dd>
      <dt>{{ $t('user.PROFILE.THEME_MODE.LABEL') }}:</dt>
      <dd>{{ $t(`user.PROFILE.THEME_MODE.VALUES.${darkMode}`) }}</dd>
      <dt>{{ $t('user.PROFILE.TIMEZONE') }}:</dt>
      <dd>{{ timezone }}</dd>
      <dt>{{ $t('user.PROFILE.DATE_FORMAT') }}:</dt>
      <dd>{{ getDateFormat(date_format, appLanguage) }}</dd>
      <dt>{{ $t('user.PROFILE.FIRST_DAY_OF_WEEK') }}:</dt>
      <dd>{{ $t(`user.PROFILE.${fistDayOfWeek}`) }}</dd>
    </dl>
    <div class="preferences-section">{{ $t('workouts.WORKOUT', 0) }}</div>
    <dl>
      <dt>{{ $t('user.PROFILE.UNITS.LABEL') }}:</dt>
      <dd>
        {{
          $t(
            `user.PROFILE.UNITS.${user.imperial_units ? 'IMPERIAL' : 'METRIC'}`
          )
        }}
      </dd>
      <dt>{{ $t('user.PROFILE.ASCENT_DATA') }}:</dt>
      <dd>{{ $t(`common.${display_ascent}`) }}</dd>
      <dt>{{ $t('user.PROFILE.ELEVATION_CHART_START.LABEL') }}:</dt>
      <dd>
        {{
          $t(
            `user.PROFILE.ELEVATION_CHART_START.${
              user.start_elevation_at_zero ? 'ZERO' : 'MIN_ALT'
            }`
          )
        }}
      </dd>
      <dt>{{ $t('user.PROFILE.USE_RAW_GPX_SPEED.LABEL') }}:</dt>
      <dd>
        {{
          $t(
            `user.PROFILE.USE_RAW_GPX_SPEED.${
              user.use_raw_gpx_speed ? 'RAW_SPEED' : 'FILTERED_SPEED'
            }`
          )
        }}
      </dd>
      <div class="info-box raw-speed-help">
        <span>
          <i class="fa fa-info-circle" aria-hidden="true" />
          {{ $t('user.PROFILE.USE_RAW_GPX_SPEED.HELP') }}
        </span>
      </div>
    </dl>
    <div class="profile-buttons">
      <button @click="$router.push('/profile/edit/preferences')">
        {{ $t('user.PROFILE.EDIT_PREFERENCES') }}
      </button>
      <button @click="$router.push('/')">{{ $t('common.HOME') }}</button>
    </div>
  </div>
</template>

<script setup lang="ts">
  import { computed } from 'vue'
  import type { ComputedRef } from 'vue'

  import { ROOT_STORE } from '@/store/constants'
  import type { TLanguage } from '@/types/locales'
  import type { IAuthUserProfile } from '@/types/user'
  import { useStore } from '@/use/useStore'
  import { getDateFormat } from '@/utils/dates'
  import { languageLabels } from '@/utils/locales'

  interface Props {
    user: IAuthUserProfile
  }
  const props = defineProps<Props>()

  const store = useStore()

  const appLanguage: ComputedRef<TLanguage> = computed(
    () => store.getters[ROOT_STORE.GETTERS.LANGUAGE]
  )
  const userLanguage = computed(() =>
    props.user.language
      ? languageLabels[props.user.language]
      : languageLabels['en']
  )
  const fistDayOfWeek = computed(() => (props.user.weekm ? 'MONDAY' : 'SUNDAY'))
  const timezone = computed(() =>
    props.user.timezone ? props.user.timezone : 'Europe/Paris'
  )
  const date_format = computed(() =>
    props.user.date_format ? props.user.date_format : 'MM/dd/yyyy'
  )
  const display_ascent = computed(() =>
    props.user.display_ascent ? 'DISPLAYED' : 'HIDDEN'
  )
  const darkMode = computed(() =>
    props.user.use_dark_mode === true
      ? 'DARK'
      : props.user.use_dark_mode === false
        ? 'LIGHT'
        : 'DEFAULT'
  )
</script>

<style lang="scss" scoped>
  @import '~@/scss/vars.scss';
  #user-preferences {
    padding-top: $default-padding;
    .preferences-section {
      font-weight: bold;
      text-transform: uppercase;
      border-bottom: 1px solid var(--card-border-color);
    }
    .raw-speed-help {
      margin-top: -$default-margin * 0.5;
    }
  }
</style>
