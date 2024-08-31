<template>
  <div class="chart-menu">
    <button
      class="chart-arrow transparent"
      @click="emit('arrowClick', true)"
      @keydown.enter="emit('arrowClick', true)"
      :disabled="isDisabled"
      :aria-label="$t('common.PREVIOUS')"
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
              :disabled="isDisabled"
            />
            <span
              :id="`frame-${frame}`"
              :tabindex="isDisabled ? -1 : 0"
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
      :disabled="isDisabled"
      :aria-label="$t('common.NEXT')"
    >
      <i class="fa fa-chevron-right" aria-hidden="true" />
    </button>
  </div>
  <div class="stats-type">
    <div class="stats-type-radio">
      <label>
        <input
          type="radio"
          name="stats_type"
          value="total"
          :checked="selectedStatsType === 'total'"
          :disabled="isDisabled"
          @click="updateStatsType"
        />
        {{ $t('common.TOTAL') }}
      </label>
      <label>
        <input
          type="radio"
          name="stats_type"
          value="average"
          :checked="selectedStatsType === 'average'"
          :disabled="isDisabled"
          @click="updateStatsType"
        />
        {{ $t('statistics.AVERAGE') }}
      </label>
    </div>
  </div>
</template>

<script setup lang="ts">
  import { ref, toRefs } from 'vue'
  import type { Ref } from 'vue'

  import type {
    TStatisticsTimeFrame,
    TStatisticsType,
  } from '@/types/statistics'

  interface Props {
    isDisabled: boolean
  }
  const props = defineProps<Props>()
  const { isDisabled } = toRefs(props)

  const emit = defineEmits(['arrowClick', 'statsTypeUpdate', 'timeFrameUpdate'])

  const selectedTimeFrame: Ref<TStatisticsTimeFrame> = ref('month')
  const timeFrames: TStatisticsTimeFrame[] = ['week', 'month', 'year']
  const selectedStatsType: Ref<TStatisticsType> = ref('total')

  function onUpdateTimeFrame(timeFrame: TStatisticsTimeFrame) {
    selectedTimeFrame.value = timeFrame
    emit('timeFrameUpdate', timeFrame)
  }
  function updateStatsType(event: Event) {
    selectedStatsType.value = (event.target as HTMLInputElement)
      .value as TStatisticsType
    emit('statsTypeUpdate', selectedStatsType.value)
  }
</script>

<style lang="scss" scoped>
  @import '~@/scss/vars';

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

      @media screen and (max-width: $x-small-limit) {
        padding: 6px;
      }
    }
  }
  .stats-type {
    display: flex;
    justify-content: center;
    margin: $default-margin 0 $default-margin * 0.5;
    .stats-type-radio {
      display: flex;
      gap: $default-padding;
      label {
        font-size: 0.9em;
        font-weight: normal;
        text-transform: lowercase;
      }
    }
  }
</style>
