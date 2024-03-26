<template>
  <div class="error-message">
    <ul v-if="Array.isArray(message)">
      <li v-for="(subMessage, index) in message" :key="index">
        {{ $t(subMessage) }}
      </li>
    </ul>
    <div v-else-if="typeof message === 'string'">
      {{ $t(message) }}
    </div>
    <div v-else>
      {{
        $t(`equipments.ERRORS.${message.status}`, {
          equipmentId: message.equipment_id,
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
  }
  const props = defineProps<Props>()
  const { message } = toRefs(props)
</script>

<style scoped lang="scss">
  @import '~@/scss/vars.scss';
  .error-message {
    background: var(--error-background-color);
    color: var(--error-color);

    border-radius: 4px;

    margin: $default-margin;
    padding: $default-padding;
  }
</style>
