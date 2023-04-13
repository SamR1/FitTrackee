<template>
  <div id="users" class="view" v-if="authUser.username">
    <div class="container">
      <UsersList :authUser="authUser" />
    </div>
  </div>
</template>

<script setup lang="ts">
  import { computed, ComputedRef } from 'vue'

  import UsersList from '@/components/Users/UsersList.vue'
  import { AUTH_USER_STORE } from '@/store/constants'
  import { IAuthUserProfile } from '@/types/user'
  import { useStore } from '@/use/useStore'

  const store = useStore()
  const authUser: ComputedRef<IAuthUserProfile> = computed(
    () => store.getters[AUTH_USER_STORE.GETTERS.AUTH_USER_PROFILE]
  )
</script>
