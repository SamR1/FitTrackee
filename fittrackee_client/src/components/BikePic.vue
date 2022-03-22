<template>
  <div id="bike">
    <img class="bike-img" :src="'/img/bike.svg'" alt="mountain bike" />
  </div>
</template>

<style scoped lang="scss">
  @import '~@/scss/vars.scss';

  #bike {
    display: flex;
    justify-content: center;

    padding: $default-padding;
    height: 100%;

    .bike-img {
      max-width: 40%;
    }
  }
</style>
