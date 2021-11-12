<template>
  <div id="user-profile-edition" class="center-card">
    <Card>
      <template #title>
        {{ $t(`user.PROFILE.${tab}_EDITION`) }}
      </template>
      <template #content>
        <UserProfileTabs
          :tabs="tabs"
          :selectedTab="tab"
          :edition="true"
          :disabled="loading"
        />
        <router-view :user="user"></router-view>
      </template>
    </Card>
  </div>
</template>

<script setup lang="ts">
  import { computed, toRefs } from 'vue'

  import UserProfileTabs from '@/components/User/UserProfileTabs.vue'
  import { AUTH_USER_STORE } from '@/store/constants'
  import { IUserProfile } from '@/types/user'
  import { useStore } from '@/use/useStore'

  interface Props {
    user: IUserProfile
    tab: string
  }
  const props = defineProps<Props>()

  const store = useStore()

  const { user, tab } = toRefs(props)
  const tabs = ['PROFILE', 'PICTURE', 'PREFERENCES', 'SPORTS']
  const loading = computed(
    () => store.getters[AUTH_USER_STORE.GETTERS.USER_LOADING]
  )
</script>
