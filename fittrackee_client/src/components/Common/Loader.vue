<template>
  <div class="loader" />
</template>

<style scoped lang="scss">
  @import '~@/scss/base';
  .loader {
    animation: spin 2s linear infinite;
    border: 14px solid var(--app-loading-color);
    border-top: 14px solid var(--app-loading-top-color);
    border-radius: 50%;
    height: 60px;
    margin-left: 41%;
    width: 60px;
  }
  @keyframes spin {
    0% {
      transform: rotate(0deg);
    }
    100% {
      transform: rotate(360deg);
    }
  }
</style>
