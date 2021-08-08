<template>
  <div id="login">
    <div class="container">
      <div class="container-sub">
        <BikePic />
      </div>
      <div class="container-sub">
        <LoginForm />
      </div>
    </div>
  </div>
</template>

<script lang="ts">
  import { defineComponent } from 'vue'
  import BikePic from '@/components/BikePic.vue'
  import LoginForm from '@/components/User/LoginForm.vue'

  export default defineComponent({
    name: 'NavBar',
    components: {
      BikePic,
      LoginForm,
    },
  })
</script>

<style lang="scss">
  @import '~@/scss/base';

  #login {
    height: 84vh;
    .container {
      display: flex;
      flex-direction: row;
      flex-wrap: wrap;
      justify-content: space-evenly;

      .container-sub {
        min-width: 50%;
      }

      @media screen and (max-width: $medium-limit) {
        flex-direction: column;
        flex-wrap: nowrap;

        .container-sub {
          .bike-img {
            margin-top: $default-margin * 1.5;
          }
        }
      }
    }
  }
</style>
