<template>
  <div class="chart-menu">
    <div class="chart-arrow">
      <i
        class="fa fa-chevron-left"
        aria-hidden="true"
        @click="emit('arrowClick', true)"
      />
    </div>
    <div class="time-frames">
      <div class="time-frames-checkboxes">
        <div v-for="frame in timeFrames" class="time-frame" :key="frame">
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

    .time-frames {
      display: flex;
      justify-content: space-around;

      .time-frames-checkboxes {
        display: inline-flex;

        .time-frame {
          label {
            font-weight: normal;
            float: left;
            padding: 0 5px;
            cursor: pointer;
          }

          label input {
            display: none;
          }

          label span {
            border: solid 1px var(--time-frame-border-color);
            border-radius: 9%;
            display: block;
            font-size: 0.9em;
            padding: 2px 6px;
            text-align: center;
          }

          input:checked + span {
            background-color: var(--time-frame-checked-bg-color);
            color: var(--time-frame-checked-color);
          }
        }
      }
    }
  }
</style>
