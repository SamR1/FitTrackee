<template>
  <div id="archive-uploads">
    <router-view :authUser="user"></router-view>
  </div>
</template>

<script setup lang="ts">
  import { onUnmounted, toRefs } from 'vue'

  import { AUTH_USER_STORE } from '@/store/constants'
  import type { IPagination } from '@/types/api.ts'
  import type { IAuthUserProfile } from '@/types/user'
  import { useStore } from '@/use/useStore'

  interface Props {
    user: IAuthUserProfile
  }
  const props = defineProps<Props>()
  const { user } = toRefs(props)

  const store = useStore()

  onUnmounted(() => {
    store.commit(AUTH_USER_STORE.MUTATIONS.SET_ARCHIVE_UPLOAD_TASKS, [])
    store.commit(
      AUTH_USER_STORE.MUTATIONS.SET_ARCHIVE_UPLOAD_TASKS_PAGINATION,
      {} as IPagination
    )
  })
</script>
