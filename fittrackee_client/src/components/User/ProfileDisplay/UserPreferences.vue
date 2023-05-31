<template>
  <div id="user-preferences" class="description-list">
    <p class="preferences-section">{{ $t('user.PROFILE.INTERFACE') }}</p>
    <dl>
      <dt>{{ $t('user.PROFILE.LANGUAGE') }}:</dt>
      <dd>{{ userLanguage }}</dd>
      <dt>{{ $t('user.PROFILE.TIMEZONE') }}:</dt>
      <dd>{{ timezone }}</dd>
      <dt>{{ $t('user.PROFILE.DATE_FORMAT') }}:</dt>
      <dd>{{ getDateFormat(date_format, appLanguage) }}</dd>
      <dt>{{ $t('user.PROFILE.FIRST_DAY_OF_WEEK') }}:</dt>
      <dd>{{ $t(`user.PROFILE.${fistDayOfWeek}`) }}</dd>
    </dl>
    <p class="preferences-section">{{ $t('user.PROFILE.TABS.ACCOUNT') }}</p>
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
    <p class="preferences-section">{{ $t('workouts.WORKOUT') }}</p>
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
      <dt>{{ $t('privacy.WORKOUTS_VISIBILITY') }}:</dt>
      <dd>
        {{ $t(`privacy.LEVELS.${user.workouts_visibility}`) }}
      </dd>
      <dt>{{ $t('privacy.MAP_VISIBILITY') }}:</dt>
      <dd>
        {{ $t(`privacy.LEVELS.${user.map_visibility}`) }}
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
  import { ComputedRef, computed, toRefs } from 'vue'

  import { ROOT_STORE } from '@/store/constants'
  import { IAuthUserProfile } from '@/types/user'
  import { useStore } from '@/use/useStore'
  import { getDateFormat } from '@/utils/dates'
  import { languageLabels } from '@/utils/locales'
  interface Props {
    user: IAuthUserProfile
  }
  const props = defineProps<Props>()

  const { user } = toRefs(props)
  const store = useStore()

  const appLanguage: ComputedRef<string> = computed(
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
</script>

<style lang="scss" scoped>
  @import '~@/scss/vars.scss';
  #user-preferences {
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
