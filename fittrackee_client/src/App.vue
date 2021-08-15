<template>
  <NavBar />
  <div class="app-container">
    <router-view />
  </div>
  <Footer />
</template>

<script lang="ts">
  import { defineComponent, onBeforeMount } from 'vue'

  import { ROOT_STORE } from '@/store/constants'
  import { useStore } from '@/use/useStore'
  import Footer from '@/components/Footer.vue'
  import NavBar from '@/components/NavBar.vue'

  export default defineComponent({
    name: 'App',
    components: {
      Footer,
      NavBar,
    },
    setup() {
      const store = useStore()
      onBeforeMount(() =>
        store.dispatch(ROOT_STORE.ACTIONS.GET_APPLICATION_CONFIG)
      )
    },
  })
</script>

<style lang="scss">
  @import '~@/scss/base';
  .app-container {
    height: $app-height;
  }
</style>
