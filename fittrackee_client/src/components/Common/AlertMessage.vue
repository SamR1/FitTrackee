<template>
  <div class="alert-message">
    <div v-html="$t(message)" />
  </div>
</template>

<script lang="ts">
  import { defineComponent } from 'vue'

  export default defineComponent({
    name: 'AlertMessage',
    props: {
      message: String,
    },
  })
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
