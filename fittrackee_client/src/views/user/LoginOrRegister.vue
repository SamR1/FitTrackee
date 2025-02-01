<template>
  <div id="loginOrRegister" class="view">
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

<script setup lang="ts">
  import { toRefs } from 'vue'

  import BikePic from '@/components/BikePic.vue'
  import LoginOrRegisterForm from '@/components/User/UserAuthForm.vue'

  interface Props {
    action: string
  }
  const props = defineProps<Props>()
  const { action } = toRefs(props)
</script>

<style lang="scss" scoped>
  @use '~@/scss/vars.scss' as *;

  #loginOrRegister {
    display: flex;

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
