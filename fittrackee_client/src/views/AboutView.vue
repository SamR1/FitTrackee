<template>
  <div id="about" class="view">
    <div class="container">
      <div class="container-sub">
        <BikePic />
      </div>
      <div class="container-sub about-details">
        <About />
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup>
  import About from '@/components/About.vue'
  import BikePic from '@/components/BikePic.vue'
</script>

<style lang="scss" scoped>
  @use '~@/scss/vars.scss' as *;

  #about {
    display: flex;
    height: 100%;

    .container {
      display: flex;
      flex-direction: row;
      justify-content: space-evenly;
      margin-bottom: $default-margin * 2;
      width: 100%;

      .container-sub {
        min-width: 50%;
        height: 100%;
      }
      .about-details {
        width: 100%;
      }
    }
    @media screen and (max-width: $medium-limit) {
      height: auto;
      .container {
        .container-sub {
          align-items: center;
          .bike-img {
            max-width: 60%;
          }
        }
      }
    }
    @media screen and (max-width: $small-limit) {
      .container {
        flex-direction: column;
      }
    }
  }
</style>
