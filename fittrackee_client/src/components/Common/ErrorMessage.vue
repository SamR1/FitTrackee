<template>
  <div class="error-message">
    <ul v-if="Array.isArray(message)">
      <li v-for="(subMessage, index) in message" :key="index">
        {{ $t(subMessage) }}
      </li>
    </ul>
    <div v-else>{{ $t(message) }}</div>
  </div>
</template>

<script lang="ts">
  import { defineComponent } from 'vue'

  export default defineComponent({
    name: 'ErrorMessage',
    props: {
      message: [String, Array],
    },
  })
</script>

<style scoped lang="scss">
  @import '~@/scss/base';
  .error-message {
    background: var(--error-background-color);
    color: var(--error-color);

    border-radius: 4px;

    margin: $default-margin;
    padding: $default-padding;
  }
</style>
