<template>
  <div
    class="calendar-workout"
    @click="
      $router.push({ name: 'Workout', params: { workoutId: workout.id } })
    "
  >
    <img alt="workout sport logo" :src="sportImg" :title="workout.title" />
    <sup>
      <i
        v-if="workout.records.length > 0"
        class="fa fa-trophy custom-fa-small"
        aria-hidden="true"
        :title="
          workout.records.map(
            (record) => ` ${t(`workouts.RECORD_${record.record_type}`)}`
          )
        "
      />
    </sup>
  </div>
</template>

<script lang="ts">
  import { defineComponent, PropType } from 'vue'
  import { useI18n } from 'vue-i18n'

  import { IWorkout } from '@/types/workouts'

  export default defineComponent({
    name: 'CalendarWorkouts',
    props: {
      workout: {
        type: Object as PropType<IWorkout>,
        required: true,
      },
      sportImg: {
        type: String,
        required: true,
      },
    },
    setup() {
      const { t } = useI18n()
      return { t }
    },
  })
</script>

<style lang="scss">
  @import '~@/scss/base';

  .calendar-workout {
    padding: 2px 0;
    cursor: pointer;
    img {
      max-width: 18px;
      max-height: 18px;
    }
    sup {
      position: relative;
      top: -0.6em;
      left: -0.4em;
      .custom-fa-small {
        font-size: 0.7em;
      }
    }

    @media screen and (max-width: $small-limit) {
      img {
        max-width: 14px;
        max-height: 14px;
      }
      sup {
        .custom-fa-small {
          font-size: 0.6em;
        }
      }
    }
  }
</style>
