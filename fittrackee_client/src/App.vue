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
  /* pt-sans-regular - latin */
  @font-face {
    font-family: 'PT Sans';
    font-style: normal;
    font-weight: 400;
    src: url('assets/fonts/pt-sans-v9-latin-regular.eot'); /* IE9 Compat Modes */
    src: local('PT Sans'), local('PTSans-Regular'),
      url('assets/fonts/pt-sans-v9-latin-regular.eot?#iefix')
        format('embedded-opentype'),
      /* IE6-IE8 */ url('assets/fonts/pt-sans-v9-latin-regular.woff2')
        format('woff2'),
      /* Super Modern Browsers */
        url('assets/fonts/pt-sans-v9-latin-regular.woff') format('woff'),
      /* Modern Browsers */ url('assets/fonts/pt-sans-v9-latin-regular.ttf')
        format('truetype'),
      /* Safari, Android, iOS */
        url('assets/fonts/pt-sans-v9-latin-regular.svg#PTSans') format('svg'); /* Legacy iOS */
  }

  /* pt-sans-italic - latin */
  @font-face {
    font-family: 'PT Sans';
    font-style: italic;
    font-weight: 400;
    src: url('assets/fonts/pt-sans-v9-latin-italic.eot'); /* IE9 Compat Modes */
    src: local('PT Sans Italic'), local('PTSans-Italic'),
      url('assets/fonts/pt-sans-v9-latin-italic.eot?#iefix')
        format('embedded-opentype'),
      /* IE6-IE8 */ url('assets/fonts/pt-sans-v9-latin-italic.woff2')
        format('woff2'),
      /* Super Modern Browsers */
        url('assets/fonts/pt-sans-v9-latin-italic.woff') format('woff'),
      /* Modern Browsers */ url('assets/fonts/pt-sans-v9-latin-italic.ttf')
        format('truetype'),
      /* Safari, Android, iOS */
        url('assets/fonts/pt-sans-v9-latin-italic.svg#PTSans') format('svg'); /* Legacy iOS */
  }

  /* pt-sans-700 - latin */
  @font-face {
    font-family: 'PT Sans';
    font-style: normal;
    font-weight: 700;
    src: url('assets/fonts/pt-sans-v9-latin-700.eot'); /* IE9 Compat Modes */
    src: local('PT Sans Bold'), local('PTSans-Bold'),
      url('assets/fonts/pt-sans-v9-latin-700.eot?#iefix')
        format('embedded-opentype'),
      /* IE6-IE8 */ url('assets/fonts/pt-sans-v9-latin-700.woff2')
        format('woff2'),
      /* Super Modern Browsers */ url('assets/fonts/pt-sans-v9-latin-700.woff')
        format('woff'),
      /* Modern Browsers */ url('assets/fonts/pt-sans-v9-latin-700.ttf')
        format('truetype'),
      /* Safari, Android, iOS */
        url('assets/fonts/pt-sans-v9-latin-700.svg#PTSans') format('svg'); /* Legacy iOS */
  }

  body {
    margin: 0;
  }

  #app {
    font-family: 'PT Sans', Helvetica, Arial, sans-serif;
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
