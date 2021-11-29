<template>
  <div
    id="workout-weather"
    v-if="workoutObject.weatherStart && workoutObject.weatherEnd"
  >
    <table class="weather-table">
      <thead>
        <tr>
          <th />
          <th>
            <div class="weather-th">
              {{ $t('workouts.START') }}
              <img
                class="weather-img"
                :src="`/img/weather/${workoutObject.weatherStart.icon}.svg`"
                :alt="
                  $t(
                    `workouts.WEATHER.DARK_SKY.${workoutObject.weatherStart.icon}`
                  )
                "
                :title="
                  $t(
                    `workouts.WEATHER.DARK_SKY.${workoutObject.weatherStart.icon}`
                  )
                "
              />
            </div>
          </th>
          <th>
            <div class="weather-th">
              {{ $t('workouts.END') }}
              <img
                class="weather-img"
                :src="`/img/weather/${workoutObject.weatherEnd.icon}.svg`"
                :alt="
                  $t(
                    `workouts.WEATHER.DARK_SKY.${workoutObject.weatherEnd.icon}`
                  )
                "
                :title="
                  $t(
                    `workouts.WEATHER.DARK_SKY.${workoutObject.weatherEnd.icon}`
                  )
                "
              />
            </div>
          </th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>
            <img
              class="weather-img weather-img-small"
              src="/img/weather/temperature.svg"
              :alt="$t(`workouts.WEATHER.TEMPERATURE`)"
              :title="$t(`workouts.WEATHER.TEMPERATURE`)"
            />
          </td>
          <td>
            {{ Number(workoutObject.weatherStart.temperature).toFixed(1) }}°C
          </td>
          <td>
            {{ Number(workoutObject.weatherEnd.temperature).toFixed(1) }}°C
          </td>
        </tr>
        <tr>
          <td>
            <img
              class="weather-img weather-img-small"
              src="/img/weather/pour-rain.svg"
              :alt="$t(`workouts.WEATHER.HUMIDITY`)"
              :title="$t(`workouts.WEATHER.HUMIDITY`)"
            />
          </td>
          <td>
            {{ Number(workoutObject.weatherStart.humidity * 100).toFixed(1) }}%
          </td>
          <td>
            {{ Number(workoutObject.weatherEnd.humidity * 100).toFixed(1) }}%
          </td>
        </tr>
        <tr>
          <td>
            <img
              class="weather-img weather-img-small"
              src="/img/weather/breeze.svg"
              :alt="$t(`workouts.WEATHER.WIND`)"
              :title="$t(`workouts.WEATHER.WIND`)"
            />
          </td>
          <td>
            <Distance
              :distance="workoutObject.weatherStart.wind"
              unitFrom="m"
              :digits="1"
              :displayUnit="false"
              :useImperialUnits="useImperialUnits"
            />
            {{ useImperialUnits ? 'ft' : 'm' }}/s
          </td>
          <td>
            <Distance
              :distance="workoutObject.weatherEnd.wind"
              unitFrom="m"
              :digits="1"
              :displayUnit="false"
              :useImperialUnits="useImperialUnits"
            />
            {{ useImperialUnits ? 'ft' : 'm' }}/s
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup lang="ts">
  import { toRefs } from 'vue'

  import { IWorkoutObject } from '@/types/workouts'

  interface Props {
    workoutObject: IWorkoutObject
    useImperialUnits: boolean
  }
  const props = defineProps<Props>()

  const { useImperialUnits, workoutObject } = toRefs(props)
</script>

<style lang="scss" scoped>
  @import '~@/scss/vars.scss';
  #workout-weather {
    padding-top: $default-padding;
    .weather-img {
      height: 30px;
      filter: var(--workout-img-color);
    }
    .weather-img-small {
      height: 20px;
    }
    .weather-table {
      width: 100%;
      text-align: center;

      .weather-th {
        display: flex;
        flex-direction: column;
        text-transform: capitalize;
      }

      tbody {
        font-size: 0.8em;
      }
    }
  }
</style>
