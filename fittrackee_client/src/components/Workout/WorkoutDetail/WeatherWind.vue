<template>
  <div class="wind">
    {{ useImperialUnits ? 
       convert_mps_to_mph(Number(weather.wind)).toFixed(1) + ' mph' : 
       Number(weather.wind).toFixed(1) + " m/s" }}
    <div class="wind-bearing">
      <i
        v-if="weather.windBearing"
        class="fa fa-long-arrow-down"
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

  function convert_mps_to_mph(windSpeed: number): number {
    return windSpeed * 2.2369363
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
