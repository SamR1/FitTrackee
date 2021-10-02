<template>
  <div id="about">
    <img class="bike-img" :src="'/img/bike.svg'" alt="mountain bike" />
  </div>
</template>

<script>
  export default {
    name: 'About',
  }
</script>

<style scoped lang="scss">
  @import '~@/scss/base';

  #about {
    display: flex;
    justify-content: center;

    padding: $default-padding;
    height: 100%;

    .bike-img {
      max-width: 40%;
    }
  }
</style>
