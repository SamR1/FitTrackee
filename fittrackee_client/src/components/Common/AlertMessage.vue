<template>
  <div class="alert-message">
    <div v-html="t(message)" />
  </div>
</template>

<script lang="ts">
  import { defineComponent } from 'vue'
  import { useI18n } from 'vue-i18n'

  export default defineComponent({
    name: 'AlertMessage',
    props: {
      message: String,
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
  .alert-message {
    background: var(--alert-background-color);
    color: var(--alert-color);

    border-radius: 4px;

    margin: $default-margin;
    padding: $default-padding;
  }
</style>
