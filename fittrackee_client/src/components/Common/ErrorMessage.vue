<template>
  <div class="error-message">
    <ul v-if="Array.isArray(message)">
      <li v-for="(submessage, index) in message" :key="index">
        {{ t(submessage) }}
      </li>
    </ul>
    <div v-else>{{ t(message) }}</div>
  </div>
</template>

<script lang="ts">
  import { defineComponent } from 'vue'
  import { useI18n } from 'vue-i18n'

  export default defineComponent({
    name: 'ErrorMessage',
    props: {
      message: [String, Array],
    },
    setup() {
      const { t } = useI18n()
      return {
        t,
      }
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
