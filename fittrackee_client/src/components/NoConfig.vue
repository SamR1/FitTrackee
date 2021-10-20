<template>
  <div id="no-config">
    <div class="error-page">
      <div class="error-img">
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 -51 512 512">
          <g id="error">
            <path
              class="error-page-img"
              d="M 0 0 C 0 11.300781 0 399.777344 0 410 L 512 410 C 512 402.324219 512 2.425781 512 0 Z M 370 71 L 370 30 L 411 30 L 411 71 Z M 30 30 L 340 30 L 340 71 L 30 71 Z M 482 380 L 30 380 L 30 101 L 482 101 Z M 441 71 L 441 30 L 482 30 L 482 71 Z M 441 71 "
            />
            <path
              class="error-page-img"
              d="M 325.519531 297.070312 C 294.328125 265.878906 294.328125 215.125 325.519531 183.929688 L 304.304688 162.71875 C 261.417969 205.605469 261.417969 275.390625 304.304688 318.28125 Z M 325.519531 297.070312 "
            />
            <path
              class="error-page-img"
              d="M 197.089844 180 L 237.089844 180 L 237.089844 220 L 197.089844 220 Z M 197.089844 180 "
            />
            <path
              class="error-page-img"
              d="M 197.089844 261 L 237.089844 261 L 237.089844 301 L 197.089844 301 Z M 197.089844 261 "
            />
          </g>
        </svg>
      </div>
      <p class="error-message" v-html="$t('error.APP_ERROR')" />
    </div>
  </div>
</template>

<script lang="ts">
  import { defineComponent } from 'vue'
  import { useI18n } from 'vue-i18n'

  export default defineComponent({
    name: 'NoConfig',
    setup() {
      const { t } = useI18n()
      return { t }
    },
  })
</script>

<style scoped lang="scss">
  @import '~@/scss/base';

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
          .error-page-img {
            stroke: none;
            fill-rule: nonzero;
            fill: var(--app-color);
            filter: var(--svg-filter);
          }
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
