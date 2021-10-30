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

<script lang="ts">
  import { computed, defineComponent, PropType } from 'vue'

  import UserProfileTabs from '@/components/User/UserProfileTabs.vue'
  import { USER_STORE } from '@/store/constants'
  import { IUserProfile } from '@/types/user'
  import { useStore } from '@/use/useStore'

  export default defineComponent({
    name: 'ProfileEdition',
    components: {
      UserProfileTabs,
    },
    props: {
      user: {
        type: Object as PropType<IUserProfile>,
        required: true,
      },
      tab: {
        type: String,
        required: true,
      },
    },
    setup() {
      const store = useStore()
      return {
        loading: computed(() => store.getters[USER_STORE.GETTERS.USER_LOADING]),
        tabs: ['PROFILE', 'PICTURE', 'PREFERENCES'],
      }
    },
  })
</script>
