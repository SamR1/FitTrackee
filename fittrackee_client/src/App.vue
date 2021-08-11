<template>
  <NavBar />
  <router-view />
  <Footer />
</template>

<script lang="ts">
  import { defineComponent } from 'vue'

  import Footer from '@/components/Footer.vue'
  import NavBar from '@/components/NavBar.vue'

  export default defineComponent({
    name: 'App',
    components: {
      Footer,
      NavBar,
    },
  })
</script>

<style lang="scss">
  @import '~@/scss/base';
</style>
