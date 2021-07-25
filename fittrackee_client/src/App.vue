<template>
  <NavBar />
  <router-view />
</template>

<script lang="ts">
  import { defineComponent } from 'vue'
  import NavBar from '@/components/NavBar.vue'

  export default defineComponent({
    name: 'App',
    components: {
      NavBar,
    },
  })
</script>

<style lang="scss">
  body {
    margin: 0;
  }

  #app {
    font-family: Avenir, Helvetica, Arial, sans-serif;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
    color: #2c3e50;

    background: #eaeaea;

    margin: 0;
    min-height: 100vh;
  }

  a {
    color: #40578a;
    text-decoration: none;
  }
</style>
