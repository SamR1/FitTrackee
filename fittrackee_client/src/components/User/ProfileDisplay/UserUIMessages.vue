<template>
  <h1>
    {{ $t('user.PROFILE.MESSAGES_PREFERENCES') }}
  </h1>
  <div id="user-notifications" class="description-list">
    <dl>
      <dt>
        {{
          capitalize(
            $t(
              'user.PROFILE.MESSAGES.warning_about_large_number_of_workouts_on_map'
            )
          )
        }}:
      </dt>
      <dd>
        <i
          :class="`fa fa-${warningOnLargeNumberOfWorkouts ? 'check' : 'times'} fa-padding`"
          aria-hidden="true"
        />
        {{ $t(`common.${warningOnLargeNumberOfWorkouts ? 'EN' : 'DIS'}ABLED`) }}
      </dd>
    </dl>
    <div class="profile-buttons">
      <button @click="$router.push('/profile/edit/messages')">
        {{ $t('user.PROFILE.EDIT_MESSAGE_PREFERENCES') }}
      </button>
      <button @click="$router.push('/')">{{ $t('common.HOME') }}</button>
    </div>
  </div>
</template>

<script setup lang="ts">
  import { capitalize, computed, toRefs } from 'vue'
  import type { ComputedRef } from 'vue'

  import type { IAuthUserProfile } from '@/types/user'

  interface Props {
    user: IAuthUserProfile
  }
  const props = defineProps<Props>()
  const { user } = toRefs(props)

  const warningOnLargeNumberOfWorkouts: ComputedRef<boolean> = computed(
    () =>
      user.value.messages_preferences
        .warning_about_large_number_of_workouts_on_map !== false
  )
</script>

<style lang="scss" scoped>
  h1 {
    font-size: 1.05em;
    font-weight: bold;
  }
  .profile-buttons {
    flex-wrap: wrap;
  }
</style>
