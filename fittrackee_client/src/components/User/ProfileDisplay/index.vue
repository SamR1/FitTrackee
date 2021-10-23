<template>
  <div id="user-profile">
    <UserHeader :user="user" />
    <div class="box">
      <UserProfileTabs :tabs="tabs" :selectedTab="tab" :edition="false" />
      <router-view :user="user"></router-view>
    </div>
  </div>
</template>

<script lang="ts">
  import { PropType, defineComponent } from 'vue'

  import UserHeader from '@/components/User/ProfileDisplay/UserHeader.vue'
  import UserProfileTabs from '@/components/User/UserProfileTabs.vue'
  import { IAuthUserProfile } from '@/types/user'

  export default defineComponent({
    name: 'ProfileDisplay',
    components: {
      UserHeader,
      UserProfileTabs,
    },
    props: {
      user: {
        type: Object as PropType<IAuthUserProfile>,
        required: true,
      },
      tab: {
        type: String,
        required: true,
      },
    },
    setup() {
      return {
        tabs: ['PROFILE', 'PREFERENCES'],
      }
    },
  })
</script>

<style lang="scss" scoped>
  @import '~@/scss/base.scss';

  #user-profile {
    margin: auto;
    width: 700px;
    @media screen and (max-width: $medium-limit) {
      width: 100%;
      margin: 0 auto 50px auto;
    }
  }
</style>
