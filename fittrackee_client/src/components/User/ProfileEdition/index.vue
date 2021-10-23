<template>
  <div id="user-profile-edition">
    <Card>
      <template #title>{{ $t(`user.PROFILE.${tab}_EDITION`) }}</template>
      <template #content>
        <UserProfileTabs
          :tabs="tabs"
          :selectedTab="tab"
          :edition="true"
          :disabled="loading"
        />
        <UserInfosEdition v-if="tab === 'PROFILE'" :user="user" />
        <UserPreferencesEdition v-if="tab === 'PREFERENCES'" :user="user" />
        <UserPictureEdition v-if="tab === 'PICTURE'" :user="user" />
      </template>
    </Card>
  </div>
</template>

<script lang="ts">
  import { PropType, computed, defineComponent, ref } from 'vue'

  import UserInfosEdition from '@/components/User/ProfileEdition/UserInfosEdition.vue'
  import UserPictureEdition from '@/components/User/ProfileEdition/UserPictureEdition.vue'
  import UserPreferencesEdition from '@/components/User/ProfileEdition/UserPreferencesEdition.vue'
  import UserProfileTabs from '@/components/User/UserProfileTabs.vue'
  import { USER_STORE } from '@/store/constants'
  import { IAuthUserProfile } from '@/types/user'
  import { useStore } from '@/use/useStore'

  export default defineComponent({
    name: 'ProfileEdition',
    components: {
      UserInfosEdition,
      UserPictureEdition,
      UserPreferencesEdition,
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
    setup(props) {
      const store = useStore()
      const tabs = ['PROFILE', 'PICTURE', 'PREFERENCES']
      const selectedTab = ref(props.tab)
      const loading = computed(
        () => store.getters[USER_STORE.GETTERS.USER_LOADING]
      )
      return { loading, selectedTab, tabs }
    },
  })
</script>

<style lang="scss" scoped>
  @import '~@/scss/base.scss';

  #user-profile-edition {
    margin: auto;
    width: 700px;
    @media screen and (max-width: $medium-limit) {
      width: 100%;
      margin: 0 auto 50px auto;
    }
  }
</style>
