<template>
  <div class="chart-menu">
    <button
      class="chart-arrow transparent"
      @click="emit('arrowClick', true)"
      @keydown.enter="emit('arrowClick', true)"
    >
      <i class="fa fa-chevron-left" aria-hidden="true" />
    </button>
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
            <span
              :id="`frame-${frame}`"
              :tabindex="0"
              role="button"
              @keydown.enter="onUpdateTimeFrame(frame)"
            >
              {{ $t(`statistics.TIME_FRAMES.${frame}`) }}
            </span>
          </label>
        </div>
      </div>
    </div>
    <button
      class="chart-arrow transparent"
      @click="emit('arrowClick', false)"
      @keydown.enter="emit('arrowClick', false)"
    >
      <i class="fa fa-chevron-right" aria-hidden="true" />
    </button>
  </div>
</template>

<script setup lang="ts">
  import { onMounted, ref } from 'vue'

  const emit = defineEmits(['arrowClick', 'timeFrameUpdate'])

  const selectedTimeFrame = ref('month')
  const timeFrames = ['week', 'month', 'year']

  function onUpdateTimeFrame(timeFrame: string) {
    selectedTimeFrame.value = timeFrame
    emit('timeFrameUpdate', timeFrame)
  }

  onMounted(() => {
    const input = document.getElementById('frame-month')
    if (input) {
      input.focus()
    }
  })
</script>

<style lang="scss" scoped>
  .chart-menu {
    display: flex;
    align-items: center;

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
