<template>
  <div class="alert-message">
    <div v-html="$t(message)" />
  </div>
</template>

<script setup lang="ts">
  import { toRefs } from 'vue'
  const props = defineProps<{
    message: string
  }>()
  const { message } = toRefs(props)
</script>

<style scoped lang="scss">
  @import '~@/scss/base';
  .alert-message {
    background: var(--alert-background-color);
    color: var(--alert-color);

    border-radius: $border-radius;

    margin: $default-margin;
    padding: $default-padding;
  }
</style>
