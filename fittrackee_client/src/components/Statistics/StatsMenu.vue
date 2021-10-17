<template>
  <div class="chart-menu">
    <div class="chart-arrow">
      <i
        class="fa fa-chevron-left"
        aria-hidden="true"
        @click="emit('arrowClick', true)"
      />
    </div>
    <div class="time-frames custom-checkboxes-group">
      <div class="time-frames-checkboxes custom-checkboxes">
        <div
          v-for="frame in timeFrames"
          class="time-frame custom-checkbox"
          :key="frame"
        >
          <label>
            <input
              type="radio"
              :id="frame"
              :name="frame"
              :checked="selectedTimeFrame === frame"
              @input="onUpdateTimeFrame(frame)"
            />
            <span>{{ t(`statistics.TIME_FRAMES.${frame}`) }}</span>
          </label>
        </div>
      </div>
    </div>
    <div class="chart-arrow">
      <i
        class="fa fa-chevron-right"
        aria-hidden="true"
        @click="emit('arrowClick', false)"
      />
    </div>
  </div>
</template>

<script lang="ts">
  import { defineComponent, ref } from 'vue'
  import { useI18n } from 'vue-i18n'

  export default defineComponent({
    name: 'StatsMenu',
    emits: ['arrowClick', 'timeFrameUpdate'],
    setup(props, { emit }) {
      const { t } = useI18n()
      let selectedTimeFrame = ref('month')
      const timeFrames = ['week', 'month', 'year']

      function onUpdateTimeFrame(timeFrame: string) {
        selectedTimeFrame.value = timeFrame
        emit('timeFrameUpdate', timeFrame)
      }

      return {
        selectedTimeFrame,
        t,
        timeFrames,
        onUpdateTimeFrame,
        emit,
      }
    },
  })
</script>

<style lang="scss" scoped>
  @import '~@/scss/base';

  .chart-menu {
    display: flex;

    .chart-arrow,
    .time-frames {
      flex-grow: 1;
      text-align: center;
    }

    .chart-arrow {
      cursor: pointer;
    }
  }
</style>
