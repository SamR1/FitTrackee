<template>
  <div id="oauth2-apps">
    <router-view :authUser="user"></router-view>
  </div>
</template>

<script setup lang="ts">
  import { onUnmounted, toRefs } from 'vue'

  import { OAUTH2_STORE, ROOT_STORE } from '@/store/constants'
  import { IAuthUserProfile } from '@/types/user'
  import { useStore } from '@/use/useStore'

  interface Props {
    user: IAuthUserProfile
  }
  const props = defineProps<Props>()

  const store = useStore()

  const { user } = toRefs(props)

  onUnmounted(() => {
    store.commit(ROOT_STORE.MUTATIONS.EMPTY_ERROR_MESSAGES)
    store.commit(OAUTH2_STORE.MUTATIONS.SET_CLIENTS, [])
  })
</script>
