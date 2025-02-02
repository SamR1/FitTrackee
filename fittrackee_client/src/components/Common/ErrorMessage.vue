<template>
  <div class="error-message" :class="{ 'no-margin': noMargin }">
    <ul v-if="Array.isArray(message)">
      <li v-for="(subMessage, index) in message" :key="index">
        {{ $t(subMessage) }}
      </li>
    </ul>
    <div v-else-if="typeof message === 'string'">
      {{ $t(message).replace('api.ERROR.', '') }}
    </div>
    <div v-else>
      {{
        $t(`equipments.ERRORS.${message.status}`, {
          equipmentId: message.equipmentId,
          equipmentLabel: message.equipmentLabel,
        })
      }}
    </div>
  </div>
</template>

<script setup lang="ts">
  import { toRefs } from 'vue'

  import type { IEquipmentError } from '@/types/equipments'

  interface Props {
    message: string | string[] | IEquipmentError
    noMargin?: boolean
  }
  const props = withDefaults(defineProps<Props>(), { noMargin: false })
  const { message } = toRefs(props)
</script>

<style scoped lang="scss">
  @use '~@/scss/vars.scss' as *;
  .error-message {
    background: var(--error-background-color);
    color: var(--error-color);

    border-radius: 4px;

    margin: $default-margin;
    padding: $default-padding;

    &.no-margin {
      margin: $default-margin 0;
    }
  }
</style>
