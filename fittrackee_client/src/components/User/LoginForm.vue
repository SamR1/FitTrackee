<template>
  <div id="login-form">
    <UserForm action="login"></UserForm>
  </div>
</template>

<script lang="ts">
  import { defineComponent } from 'vue'
  import UserForm from '@/components/User/UserForm.vue'

  export default defineComponent({
    name: 'LoginForm',
    components: {
      UserForm,
    },
  })
</script>

<style scoped lang="scss">
  @import '~@/scss/base';

  #login-form {
    display: flex;
    align-items: center;
    height: calc(100vh - 100px);

    border-radius: 4px;
    margin: $default-margin 0;

    @media screen and (max-width: $medium-limit) {
      height: auto;
    }
  }
</style>
