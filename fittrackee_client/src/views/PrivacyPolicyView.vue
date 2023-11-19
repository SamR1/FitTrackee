<template>
  <div id="privacy-policy" class="view">
    <div class="container">
      <PrivacyPolicy />
    </div>
    <div id="bottom" />
  </div>
</template>

<script lang="ts" setup>
  import { onBeforeMount } from 'vue'

  import PrivacyPolicy from '@/components/PrivacyPolicy.vue'
  import { ROOT_STORE } from '@/store/constants'
  import { useStore } from '@/use/useStore'

  const store = useStore()

  onBeforeMount(() => {
    store.dispatch(ROOT_STORE.ACTIONS.GET_APPLICATION_PRIVACY_POLICY)
  })
</script>
