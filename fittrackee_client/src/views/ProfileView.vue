<template>
  <div id="profile" class="container" v-if="authUser.username">
    <ProfileEdition :user="authUser" v-if="edition" />
    <Profile :user="authUser" v-else />
  </div>
</template>

<script lang="ts">
  import { computed, ComputedRef, defineComponent } from 'vue'

  import Profile from '@/components/User/Profile.vue'
  import ProfileEdition from '@/components/User/ProfileEdition.vue'
  import { USER_STORE } from '@/store/constants'
  import { IAuthUserProfile } from '@/types/user'
  import { useStore } from '@/use/useStore'

  export default defineComponent({
    name: 'ProfileView',
    components: {
      Profile,
      ProfileEdition,
    },
    props: {
      edition: {
        type: Boolean,
        required: true,
      },
    },
    setup() {
      const store = useStore()
      const authUser: ComputedRef<IAuthUserProfile> = computed(
        () => store.getters[USER_STORE.GETTERS.AUTH_USER_PROFILE]
      )
      return {
        authUser,
      }
    },
  })
</script>

<style lang="scss" scoped>
  @import '~@/scss/base.scss';
  #profile {
    display: flex;
    flex-direction: column;
  }
</style>
