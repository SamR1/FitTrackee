<template>
  <div id="error">
    <div class="error-content">
      <h1>{{ title }}</h1>
      <p>{{ message }}</p>
      <button v-if="buttonText" @click="$router.push(path)" class="upper">
        {{ buttonText }}
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
  import { toRefs } from 'vue'

  interface Props {
    title: string
    message: string
    buttonText: string
    path?: string
  }
  const props = withDefaults(defineProps<Props>(), {
    path: '/',
  })
  const { buttonText, title, message, path } = toRefs(props)
</script>

<style scoped lang="scss">
  #error {
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
