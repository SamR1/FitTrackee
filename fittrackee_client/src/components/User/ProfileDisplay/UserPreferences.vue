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
      <dd>{{ dateFormat }}</dd>
      <dt>{{ $t('user.PROFILE.FIRST_DAY_OF_WEEK') }}:</dt>
      <dd>{{ $t(`user.PROFILE.${fistDayOfWeek}`) }}</dd>
    </dl>
    <div class="preferences-section">{{ $t('user.PROFILE.TABS.ACCOUNT') }}</div>
    <dl>
      <dt>{{ $t('user.PROFILE.FOLLOW_REQUESTS_APPROVAL.LABEL') }}:</dt>
      <dd>
        {{
          $t(
            `user.PROFILE.FOLLOW_REQUESTS_APPROVAL.${
              user.manually_approves_followers ? 'MANUALLY' : 'AUTOMATICALLY'
            }`
          )
        }}
      </dd>
      <dt>{{ $t('user.PROFILE.PROFILE_IN_USERS_DIRECTORY.LABEL') }}:</dt>
      <dd>
        {{
          $t(
            `user.PROFILE.PROFILE_IN_USERS_DIRECTORY.${
              user.hide_profile_in_users_directory ? 'HIDDEN' : 'DISPLAYED'
            }`
          )
        }}
      </dd>
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
    <dl>
      <dt>{{ $t('visibility_levels.WORKOUTS_VISIBILITY') }}:</dt>
      <dd>
        {{ $t(`visibility_levels.LEVELS.${user.workouts_visibility}`) }}
      </dd>
      <dt>{{ $t('visibility_levels.ANALYSIS_VISIBILITY') }}:</dt>
      <dd>
        {{ $t(`visibility_levels.LEVELS.${user.analysis_visibility}`) }}
      </dd>
      <dt>{{ $t('visibility_levels.MAP_VISIBILITY') }}:</dt>
      <dd>
        {{ $t(`visibility_levels.LEVELS.${user.map_visibility}`) }}
      </dd>
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
  import { computed, toRefs } from 'vue'
  import type { ComputedRef } from 'vue'

  import useAuthUser from '@/composables/useAuthUser'
  import type { IAuthUserProfile } from '@/types/user'
  import { languageLabels } from '@/utils/locales'

  interface Props {
    user: IAuthUserProfile
  }
  const props = defineProps<Props>()
  const { user } = toRefs(props)

  const { dateFormat, timezone } = useAuthUser()

  const userLanguage: ComputedRef<string> = computed(() =>
    user.value.language && user.value.language in languageLabels
      ? languageLabels[user.value.language]
      : languageLabels['en']
  )
  const fistDayOfWeek = computed(() => (user.value.weekm ? 'MONDAY' : 'SUNDAY'))
  const display_ascent = computed(() =>
    user.value.display_ascent ? 'DISPLAYED' : 'HIDDEN'
  )
  const darkMode = computed(() =>
    user.value.use_dark_mode === true
      ? 'DARK'
      : user.value.use_dark_mode === false
        ? 'LIGHT'
        : 'DEFAULT'
  )
</script>

<style lang="scss" scoped>
  @import '~@/scss/vars.scss';
  #user-preferences {
    padding: $default-padding * 0.5 0 $default-padding;
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
