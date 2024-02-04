<template>
  <div class="calendar-header">
    <button
      class="calendar-arrow calendar-arrow-left transparent"
      @click="emit('displayPreviousMonth')"
    >
      <i class="fa fa-chevron-left" aria-hidden="true" />
    </button>
    <div class="calendar-month">
      <span>
        {{ format(day, 'MMM yyyy', { locale: localeOptions }) }}
      </span>
    </div>
    <button
      class="calendar-arrow calendar-arrow-right transparent"
      @click="emit('displayNextMonth')"
    >
      <i class="fa fa-chevron-right" aria-hidden="true" />
    </button>
  </div>
</template>

<script setup lang="ts">
  import { format } from 'date-fns'
  import type { Locale } from 'date-fns'
  import { toRefs } from 'vue'

  interface Props {
    day: Date
    localeOptions: Locale
  }
  const props = defineProps<Props>()

  const emit = defineEmits(['displayNextMonth', 'displayPreviousMonth'])

  const { day, localeOptions } = toRefs(props)
</script>

<style lang="scss">
  @import '~@/scss/vars.scss';
  .calendar-header {
    display: flex;
    flex-direction: row;

    .calendar-arrow {
      flex-grow: 1;
      padding: $default-padding - 1 px;
    }
    .calendar-arrow-left {
      text-align: left;
      cursor: pointer;
    }
    .calendar-arrow-right {
      text-align: right;
      cursor: pointer;
    }
    .calendar-month {
      flex-grow: 1;
      font-weight: bold;
      padding: $default-padding;
      text-align: center;
      text-transform: uppercase;
    }
  }
</style>
