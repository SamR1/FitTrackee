<template>
  <div id="user-profile">
    <UserHeader :user="user" />
    <div class="box">
      <UserProfileTabs :tabs="tabGroup1" :selectedTab="tab" :edition="false" />
      <UserProfileTabs :tabs="tabGroup2" :selectedTab="tab" :edition="false" />
      <router-view :user="user"></router-view>
    </div>
  </div>
</template>

<script setup lang="ts">
  import { computed, toRefs } from 'vue'
  import type { ComputedRef } from 'vue'

  import UserHeader from '@/components/User/ProfileDisplay/UserHeader.vue'
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
  const tabGroup1 = computed(() =>
    isSuspended.value
      ? ['PROFILE', 'PREFERENCES', 'SPORTS', 'EQUIPMENTS', 'APPS', 'MODERATION']
      : ['PROFILE', 'PREFERENCES', 'SPORTS', 'EQUIPMENTS', 'APPS']
  )
  const tabGroup2 = computed(() =>
    isSuspended.value ? [] : ['FOLLOW-REQUESTS', 'BLOCKED-USERS', 'MODERATION']
  )
</script>

<style lang="scss" scoped>
  @import '~@/scss/vars.scss';

  #user-profile {
    margin: auto;
    width: 700px;
    @media screen and (max-width: $medium-limit) {
      width: 100%;
      margin: 0 auto 50px auto;
    }
  }
</style>
