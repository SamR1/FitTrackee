<template>
  <div class="alert-message">
    <span v-if="param">
      <i18n-t :keypath="message">
        <span>{{ param }}</span>
      </i18n-t>
    </span>
    <span v-else v-html="$t(message)" />
    <slot name="additionalMessage"></slot>
  </div>
</template>

<script setup lang="ts">
  import { toRefs } from 'vue'

  interface Props {
    message: string
    param?: string
  }
  const props = withDefaults(defineProps<Props>(), {
    param: () => '',
  })
  const { message, param } = toRefs(props)
</script>

<style scoped lang="scss">
  @import '~@/scss/vars.scss';
  .alert-message {
    display: flex;
    gap: 3px;
    background: var(--alert-background-color);
    color: var(--alert-color);

    border-radius: $border-radius;

    margin: $default-margin;
    padding: $default-padding;
  }
</style>
