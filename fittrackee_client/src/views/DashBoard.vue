<template>
  <div id="dashboard">
    <div class="container">
      <UserStats :user="authUser" v-if="authUser.username" />
    </div>
  </div>
</template>

<script lang="ts">
  import { computed, ComputedRef, defineComponent } from 'vue'

  import UserStats from '@/components/Dashboard/UserStats.vue'
  import { USER_STORE } from '@/store/constants'
  import { IAuthUserProfile } from '@/store/modules/user/interfaces'
  import { useStore } from '@/use/useStore'

  export default defineComponent({
    name: 'Dashboard',
    components: {
      UserStats,
    },
    setup() {
      const store = useStore()
      const authUser: ComputedRef<IAuthUserProfile> = computed(
        () => store.getters[USER_STORE.GETTERS.AUTH_USER_PROFILE]
      )
      return { authUser }
    },
  })
</script>
