// adapted from: https://css-tricks.com/building-a-donut-chart-with-vue-and-svg/
<template>
  <div class="donut-chart">
    <svg height="34" width="34" viewBox="0 0 34 34">
      <g v-for="(data, index) of Object.entries(datasets)" :key="index">
        <circle
          :cx="cx"
          :cy="cy"
          :r="radius"
          fill="transparent"
          :stroke="colors[+data[0]]"
          :stroke-dashoffset="
            calculateStrokeDashOffset(data[1].percentage, circumference)
          "
          :stroke-dasharray="circumference"
          stroke-width="3"
          stroke-opacity="0.8"
          :transform="returnCircleTransformValue(index, data[1].percentage)"
        />
      </g>
    </svg>
  </div>
</template>

<script setup lang="ts">
  import { toRefs } from 'vue'

  interface Props {
    colors: Record<number, string>
    datasets: Record<number, Record<string, number>>
  }
  const props = defineProps<Props>()
  const { colors, datasets } = toRefs(props)

  let angleOffset = -90
  const cx = 16
  const cy = 16
  const radius = 14
  const circumference = 2 * Math.PI * radius

  function calculateStrokeDashOffset(
    percentage: number,
    circumference: number
  ): number {
    return circumference - percentage * circumference
  }
  function returnCircleTransformValue(
    index: number,
    percentage: number
  ): string {
    const rotation = `rotate(${angleOffset}, ${cx}, ${cy})`
    angleOffset = percentage * 360 + angleOffset
    return rotation
  }
</script>
