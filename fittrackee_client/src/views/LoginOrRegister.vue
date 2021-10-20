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
  import LoginOrRegisterForm from '@/components/User/UserAuthForm.vue'

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
