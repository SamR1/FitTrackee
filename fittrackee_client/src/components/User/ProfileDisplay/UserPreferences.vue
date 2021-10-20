<template>
  <div id="user-preferences" class="description-list">
    <dl>
      <dt>{{ $t('user.PROFILE.LANGUAGE') }}:</dt>
      <dd>{{ language }}</dd>
    </dl>
    <dl>
      <dt>{{ $t('user.PROFILE.TIMEZONE') }}:</dt>
      <dd>{{ timezone }}</dd>
    </dl>
    <dl>
      <dt>{{ $t('user.PROFILE.FIRST_DAY_OF_WEEK') }}:</dt>
      <dd>{{ $t(`user.PROFILE.${fistDayOfWeek}`) }}</dd>
    </dl>
    <div class="profile-buttons">
      <button @click="$router.push('/profile/edit/preferences')">
        {{ $t('user.PROFILE.EDIT_PREFERENCES') }}
      </button>
      <button @click="$router.push('/')">{{ $t('common.HOME') }}</button>
    </div>
  </div>
</template>

<script lang="ts">
  import { PropType, computed, defineComponent } from 'vue'

  import { IAuthUserProfile } from '@/types/user'

  export default defineComponent({
    name: 'UserPreferences',
    props: {
      user: {
        type: Object as PropType<IAuthUserProfile>,
        required: true,
      },
    },
    setup(props) {
      const language = computed(() =>
        props.user.language ? props.user.language.toUpperCase() : 'EN'
      )
      const fistDayOfWeek = computed(() =>
        props.user.weekm ? 'MONDAY' : 'SUNDAY'
      )
      const timezone = computed(() =>
        props.user.timezone ? props.user.timezone : 'Europe/Paris'
      )
      return { fistDayOfWeek, language, timezone }
    },
  })
</script>

<style lang="scss" scoped>
  @import '~@/scss/base.scss';
  #user-preferences {
    .profile-buttons {
      display: flex;
      gap: $default-padding;
    }
  }
</style>
