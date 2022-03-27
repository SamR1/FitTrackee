<template>
  <div id="no-config">
    <div class="error-page">
      <div class="error-img">
        <ErrorImg />
      </div>
      <p class="error-message" v-html="$t('error.APP_ERROR')" />
    </div>
  </div>
</template>

<script lang="ts" setup>
  import ErrorImg from '@/components/Common/Images/ErrorImg.vue'
</script>

<style scoped lang="scss">
  @import '~@/scss/vars.scss';

  #no-config {
    display: flex;
    align-items: center;
    justify-content: space-around;

    padding: $default-padding;
    height: 100%;

    .error-page {
      display: flex;
      flex-direction: column;
      align-items: center;
      max-width: 100%;

      .error-img {
        width: 150px;

        svg {
          stroke: none;
          fill-rule: nonzero;
          fill: var(--app-color);
          filter: var(--svg-filter);
        }
      }

      .error-message {
        font-size: 1.2em;
        text-align: center;

        @media screen and (max-width: $medium-limit) {
          font-size: 1em;
        }
      }
    }
  }
</style>
