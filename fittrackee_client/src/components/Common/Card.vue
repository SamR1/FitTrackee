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

<style lang="scss">
  @import '~@/scss/vars.scss';

  .card {
    border: solid 1px var(--card-border-color);
    border-radius: $border-radius;
    margin: $default-margin;

    .card-title {
      font-weight: bold;
      border-bottom: solid 1px var(--card-border-color);
      padding: $default-padding $default-padding * 2;
    }

    .card-content {
      padding: $default-padding $default-padding * 2;
    }
  }
</style>
