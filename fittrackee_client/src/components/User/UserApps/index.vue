<template>
  <div id="oauth2-apps">
    <router-view :authUser="user"></router-view>
  </div>
</template>

<script setup lang="ts">
  import { toRefs } from 'vue'

  import { IAuthUserProfile } from '@/types/user'

  interface Props {
    user: IAuthUserProfile
  }
  const props = defineProps<Props>()

  const { user } = toRefs(props)
</script>
