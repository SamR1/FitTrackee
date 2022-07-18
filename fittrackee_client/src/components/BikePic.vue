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
    margin-top: 180px;
    padding: $default-padding;

    .bike-img {
      max-width: 200px;
    }
    @media screen and (max-width: $small-limit) {
      margin-top: $default-margin;
      .bike-img {
        max-width: 150px;
      }
    }
  }
</style>
