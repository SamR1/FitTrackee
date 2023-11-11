<template>
  <div class="calendar-days">
    <div class="calendar-day" v-for="(day, index) in days" :key="index">
      {{ format(day, 'EEE', { locale: localeOptions }) }}
    </div>
  </div>
</template>

<script setup lang="ts">
  import { format, addDays } from 'date-fns'
  import type { Locale } from 'date-fns'

  interface Props {
    startDate: Date
    localeOptions: Locale
  }
  const props = defineProps<Props>()

  const days = []
  for (let i = 0; i < 7; i++) {
    days.push(addDays(props.startDate, i))
  }
</script>

<style lang="scss">
  @import '~@/scss/vars.scss';
  .calendar-days {
    display: flex;
    flex-direction: row;
    border-top: solid 1px var(--calendar-border-color);

    .calendar-day {
      flex-grow: 1;
      padding: $default-padding * 0.5;
      text-align: center;
      text-transform: uppercase;
      color: var(--app-color-light);
    }
  }
</style>
