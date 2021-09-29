<template>
  <div class="calendar-header">
    <div
      class="calendar-arrow calendar-arrow-left"
      @click="emit('displayPreviousMonth')"
    >
      <i class="fa fa-chevron-left" aria-hidden="true" />
    </div>
    <div class="calendar-month">
      <span>
        {{ format(day, 'MMM yyyy', localeOptions) }}
      </span>
    </div>
    <div
      class="calendar-arrow calendar-arrow-right"
      @click="emit('displayNextMonth')"
    >
      <i class="fa fa-chevron-right" aria-hidden="true" />
    </div>
  </div>
</template>

<script lang="ts">
  import { format } from 'date-fns'
  import { defineComponent } from 'vue'
  export default defineComponent({
    name: 'CalendarHeader',
    props: {
      day: {
        type: Date,
        required: true,
      },
      localeOptions: {
        type: String,
        required: true,
      },
    },
    emits: ['displayNextMonth', 'displayPreviousMonth'],
    setup(props, { emit }) {
      return { emit, format }
    },
  })
</script>

<style lang="scss">
  @import '~@/scss/base';
  .calendar-header {
    display: flex;
    flex-direction: row;

    .calendar-arrow,
    .calendar-month {
      flex-grow: 1;
      padding: $default-padding;
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
      font-weight: bold;
      text-align: center;
      text-transform: uppercase;
    }
  }
</style>
