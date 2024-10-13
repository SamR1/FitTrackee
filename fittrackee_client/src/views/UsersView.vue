<template>
  <div id="users" class="view" v-if="authUser.username">
    <div class="container">
      <UsersList :authUser="authUser" />
    </div>
  </div>
</template>

<script setup lang="ts">
  import UsersList from '@/components/Users/UsersList.vue'
  import useAuthUser from '@/composables/useAuthUser'

  const { authUser } = useAuthUser()
</script>
