<template>
  <div>
    <router-view :authUser="user"></router-view>
  </div>
</template>

<script setup lang="ts">
  import { toRefs } from 'vue'

  import type { IAuthUserProfile } from '@/types/user'

  interface Props {
    user: IAuthUserProfile
  }
  const props = defineProps<Props>()
  const { user } = toRefs(props)
</script>
