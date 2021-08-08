<template>
  <div id="about">
    <img class="bike-img" v-bind:src="bike_image_url" alt="mountain bike" />
  </div>
</template>

<script lang="ts">
  import { defineComponent } from 'vue'

  export default defineComponent({
    name: 'About',
    setup() {
      return {
        bike_image_url: './img/bike.svg',
      }
    },
  })
</script>

<style scoped lang="scss">
  @import '~@/scss/base';

  #about {
    display: flex;
    justify-content: center;

    padding: $default-padding;
    height: calc(100vh - 100px);

    @media screen and (max-width: $medium-limit) {
      height: auto;
    }

    .bike-img {
      max-width: 40%;
    }
  }
</style>
