<template>
  <div class="calendar-days">
    <div class="calendar-day" v-for="(day, index) in days" :key="index">
      {{ format(day, 'EEE', localeOptions) }}
    </div>
  </div>
</template>

<script lang="ts">
  import { format, addDays } from 'date-fns'
  import { defineComponent } from 'vue'

  export default defineComponent({
    name: 'CalendarDays',
    props: {
      startDate: {
        type: Date,
        required: true,
      },
      localeOptions: {
        type: String,
        required: true,
      },
    },
    setup(props) {
      const days = []
      for (let i = 0; i < 7; i++) {
        days.push(addDays(props.startDate, i))
      }
      return { days, addDays, format }
    },
  })
</script>

<style lang="scss">
  @import '~@/scss/base';
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
