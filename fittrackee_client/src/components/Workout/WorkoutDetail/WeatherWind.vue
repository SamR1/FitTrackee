<template>
  <div class="wind">
    <Distance
      :distance="weather.wind"
      unitFrom="m"
      :digits="1"
      :displayUnit="false"
      :useImperialUnits="useImperialUnits"
    />
    {{ useImperialUnits ? 'ft' : 'm' }}/s
    <div class="wind-bearing">
      <i
        v-if="weather.windBearing"
        class="fa fa-long-arrow-up"
        :style="{
          transform: `rotate(${weather.windBearing}deg)`,
        }"
        aria-hidden="true"
        :title="getWindDirectionTitle(weather.windBearing)"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
  import { toRefs } from 'vue'
  import { useI18n } from 'vue-i18n'

  import { IWeather } from '@/types/workouts'
  import { convertDegreeToDirection } from '@/utils/weather'

  interface Props {
    weather: IWeather
    useImperialUnits: boolean
  }
  const props = defineProps<Props>()

  const { useImperialUnits, weather } = toRefs(props)
  const { t } = useI18n()

  function getWindDirectionTitle(windBearing: number): string {
    return t(
      `workouts.WEATHER.WIND_DIRECTIONS.${convertDegreeToDirection(
        windBearing
      )}`
    )
  }
</script>

<style lang="scss" scoped>
  .wind {
    display: flex;
    justify-content: center;
    .wind-bearing {
      padding-left: 5px;
    }
  }
</style>
