<template>
  <div id="loginOrRegister">
    <div class="container">
      <div class="container-sub">
        <BikePic />
      </div>
      <div class="container-sub">
        <LoginOrRegisterForm :action="action" />
      </div>
    </div>
  </div>
</template>

<script lang="ts">
  import { defineComponent } from 'vue'

  import BikePic from '@/components/BikePic.vue'
  import LoginOrRegisterForm from '@/components/User/LoginOrRegisterForm.vue'

  export default defineComponent({
    name: 'NavBar',
    components: {
      BikePic,
      LoginOrRegisterForm,
    },
    props: {
      action: {
        type: String,
        required: true,
      },
    },
  })
</script>

<style lang="scss">
  @import '~@/scss/base';

  #loginOrRegister {
    height: 100%;

    .container {
      display: flex;
      flex-direction: row;
      justify-content: space-evenly;

      height: 100%;
      margin-bottom: $default-margin * 2;

      .container-sub {
        min-width: 50%;
      }

      @media screen and (max-width: $medium-limit) {
        display: block;
        .container-sub {
          .bike-img {
            margin-top: $default-margin * 1.5;
          }
        }
      }
    }
  }
</style>
