<template>
  <div id="error404">
    <div class="error-content">
      <h1>{{ title }}</h1>
      <p>{{ message }}</p>
      <button v-if="buttonText" @click="$router.push(path)" class="upper">
        {{ buttonText }}
      </button>
    </div>
  </div>
</template>

<script lang="ts">
  import { defineComponent } from 'vue'

  export default defineComponent({
    name: 'Error',
    props: {
      title: {
        type: String,
        required: true,
      },
      message: {
        type: String,
      },
      buttonText: {
        type: String,
      },
      path: {
        type: String,
        default: '/',
      },
    },
  })
</script>

<style scoped lang="scss">
  @import '~@/scss/base';

  #error404 {
    display: flex;
    align-items: center;
    justify-content: center;

    height: 75vh;

    text-align: center;

    .error-content {
      margin-top: 50px;

      h1 {
        font-size: 6em;
        text-shadow: 4px 4px 0 var(--app-shadow-color);
      }

      p {
        font-size: 1.2em;
        margin: 30px 0;
      }
    }
  }
</style>
