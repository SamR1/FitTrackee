<template>
  <div id="user-profile">
    <UserHeader :user="user" />
    <div class="box">
      <UserProfileTabs
        v-if="tab in tabs"
        :tabs="tabs"
        :selectedTab="tab"
        :edition="false"
      />
      <router-view :user="user"></router-view>
    </div>
  </div>
</template>

<script setup lang="ts">
  import { toRefs } from 'vue'

  import UserHeader from '@/components/User/ProfileDisplay/UserHeader.vue'
  import UserProfileTabs from '@/components/User/UserProfileTabs.vue'
  import { IUserProfile } from '@/types/user'

  interface Props {
    user: IUserProfile
    tab: string
  }
  const props = defineProps<Props>()

  const { user, tab } = toRefs(props)
  const tabs = ['PROFILE', 'PREFERENCES', 'SPORTS']
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
