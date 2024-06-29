<template>
  <div id="user-profile-edition" class="center-card">
    <Card>
      <template #title>
        {{ $t(`user.PROFILE.${tab}_EDITION`) }}
      </template>
      <template #content>
        <UserProfileTabs :tabs="tabs" :selectedTab="tab" :edition="true" />
        <router-view :user="user"></router-view>
      </template>
    </Card>
  </div>
</template>

<script setup lang="ts">
  import { computed, toRefs } from 'vue'
  import type { ComputedRef } from 'vue'

  import UserProfileTabs from '@/components/User/UserProfileTabs.vue'
  import { AUTH_USER_STORE } from '@/store/constants'
  import type { IUserProfile } from '@/types/user'
  import { useStore } from '@/use/useStore'

  interface Props {
    user: IUserProfile
    tab: string
  }
  const props = defineProps<Props>()

  const { user, tab } = toRefs(props)

  const store = useStore()

  const isSuspended: ComputedRef<boolean> = computed(
    () => store.getters[AUTH_USER_STORE.GETTERS.IS_SUSPENDED]
  )
  const tabs = computed(() =>
    isSuspended.value
      ? [
          'PROFILE',
          'ACCOUNT',
          'PICTURE',
          'PREFERENCES',
          'EQUIPMENTS',
          'PRIVACY-POLICY',
        ]
      : [
          'PROFILE',
          'ACCOUNT',
          'PICTURE',
          'PREFERENCES',
          'SPORTS',
          'EQUIPMENTS',
          'PRIVACY-POLICY',
        ]
  )
</script>
