<template>
  <div id="workout-weather" v-if="workout.weather_start && workout.weather_end">
    <table class="weather-table">
      <thead>
        <tr>
          <th />
          <th>
            <div class="weather-th">
              {{ t('workouts.START') }}
              <img
                class="weather-img"
                :src="`/img/weather/${workout.weather_start.icon}.svg`"
                :alt="
                  t(`workouts.WEATHER.DARK_SKY.${workout.weather_start.icon}`)
                "
                :title="
                  t(`workouts.WEATHER.DARK_SKY.${workout.weather_start.icon}`)
                "
              />
            </div>
          </th>
          <th>
            <div class="weather-th">
              {{ t('workouts.END') }}
              <img
                class="weather-img"
                :src="`/img/weather/${workout.weather_end.icon}.svg`"
                :alt="
                  t(`workouts.WEATHER.DARK_SKY.${workout.weather_end.icon}`)
                "
                :title="
                  t(`workouts.WEATHER.DARK_SKY.${workout.weather_end.icon}`)
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
              :alt="t(`workouts.WEATHER.TEMPERATURE`)"
              :title="t(`workouts.WEATHER.TEMPERATURE`)"
            />
          </td>
          <td>{{ Number(workout.weather_start.temperature).toFixed(1) }}°C</td>
          <td>{{ Number(workout.weather_end.temperature).toFixed(1) }}°C</td>
        </tr>
        <tr>
          <td>
            <img
              class="weather-img weather-img-small"
              src="/img/weather/pour-rain.svg"
              :alt="t(`workouts.WEATHER.HUMIDITY`)"
              :title="t(`workouts.WEATHER.HUMIDITY`)"
            />
          </td>
          <td>
            {{ Number(workout.weather_start.humidity * 100).toFixed(1) }}%
          </td>
          <td>{{ Number(workout.weather_end.humidity * 100).toFixed(1) }}%</td>
        </tr>
        <tr>
          <td>
            <img
              class="weather-img weather-img-small"
              src="/img/weather/breeze.svg"
              :alt="t(`workouts.WEATHER.WIND`)"
              :title="t(`workouts.WEATHER.WIND`)"
            />
          </td>
          <td>{{ Number(workout.weather_start.wind).toFixed(1) }}m/s</td>
          <td>{{ Number(workout.weather_end.wind).toFixed(1) }}m/s</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script lang="ts">
  import { defineComponent, PropType } from 'vue'
  import { useI18n } from 'vue-i18n'

  import { IWorkout } from '@/types/workouts'
  export default defineComponent({
    name: 'WorkoutWeather',
    props: {
      workout: {
        type: Object as PropType<IWorkout>,
        required: true,
      },
    },
    setup() {
      const { t } = useI18n()
      return { t }
    },
  })
</script>

<style lang="scss" scoped>
  @import '~@/scss/base';
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
