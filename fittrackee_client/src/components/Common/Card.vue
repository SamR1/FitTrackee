<template>
  <div class="card">
    <div class="card-title">
      <slot name="title"></slot>
    </div>
    <div class="card-content">
      <slot name="content"></slot>
    </div>
  </div>
</template>

<script lang="ts">
  import { defineComponent } from 'vue'
  export default defineComponent({
    name: 'Card',
  })
</script>

<style lang="scss">
  @import '~@/scss/base';

  .card {
    border: solid 1px var(--card-border-color);
    border-radius: $border-radius;
    margin: $default-margin;
    padding: $default-padding $default-padding * 2;
  }
</style>
