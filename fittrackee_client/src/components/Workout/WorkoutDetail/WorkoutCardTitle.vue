<template>
  <div id="workout-card-title">
    <div
      class="workout-previous workout-arrow"
      :class="{ inactive: !workoutObject.previousUrl }"
      :title="
        workoutObject.previousUrl
          ? $t(`workouts.PREVIOUS_${workoutObject.type}`)
          : $t(`workouts.NO_PREVIOUS_${workoutObject.type}`)
      "
      @click="
        workoutObject.previousUrl
          ? $router.push(workoutObject.previousUrl)
          : null
      "
    >
      <i class="fa fa-chevron-left" aria-hidden="true" />
    </div>
    <div class="workout-card-title">
      <SportImage :sport-label="sport.label" />
      <div class="workout-title-date">
        <div class="workout-title" v-if="workoutObject.type === 'WORKOUT'">
          {{ workoutObject.title }}
          <i
            class="fa fa-edit"
            aria-hidden="true"
            @click="
              $router.push({
                name: 'EditWorkout',
                params: { workoutId: workoutObject.workoutId },
              })
            "
          />
          <i
            class="fa fa-trash"
            aria-hidden="true"
            @click="emit('displayModal', true)"
          />
        </div>
        <div class="workout-title" v-else>
          {{ workoutObject.title }}
          <span class="workout-segment">
            —
            <i class="fa fa-map-marker" aria-hidden="true" />
            {{ $t('workouts.SEGMENT') }}
            {{ workoutObject.segmentId + 1 }}
          </span>
        </div>
        <div class="workout-date">
          {{ workoutObject.workoutDate }} -
          {{ workoutObject.workoutTime }}
          <span class="workout-link">
            <router-link
              v-if="workoutObject.type === 'SEGMENT'"
              :to="{
                name: 'Workout',
                params: { workoutId: workoutObject.workoutId },
              }"
            >
              > {{ $t('workouts.BACK_TO_WORKOUT') }}
            </router-link></span
          >
        </div>
      </div>
    </div>
    <div
      class="workout-next workout-arrow"
      :class="{ inactive: !workoutObject.nextUrl }"
      :title="
        workoutObject.nextUrl
          ? $t(`workouts.NEXT_${workoutObject.type}`)
          : $t(`workouts.NO_NEXT_${workoutObject.type}`)
      "
      @click="
        workoutObject.nextUrl ? $router.push(workoutObject.nextUrl) : null
      "
    >
      <i class="fa fa-chevron-right" aria-hidden="true" />
    </div>
  </div>
</template>

<script lang="ts">
  import { PropType, defineComponent } from 'vue'

  import SportImage from '@/components/Common/Images/SportImage/index.vue'
  import { ISport } from '@/types/sports'
  import { IWorkoutObject } from '@/types/workouts'

  export default defineComponent({
    name: 'WorkoutCardTitle',
    components: {
      SportImage,
    },
    props: {
      sport: {
        type: Object as PropType<ISport>,
        required: true,
      },
      workoutObject: {
        type: Object as PropType<IWorkoutObject>,
        required: true,
      },
    },
    emits: ['displayModal'],
    setup(props, { emit }) {
      return { emit }
    },
  })
</script>

<style lang="scss" scoped>
  @import '~@/scss/base';

  #workout-card-title {
    display: flex;
    justify-content: space-between;
    align-items: center;

    .workout-arrow {
      cursor: pointer;
      &.inactive {
        color: var(--disabled-color);
        cursor: default;
      }
    }

    .workout-card-title {
      display: flex;
      flex-grow: 1;
      .sport-img {
        height: 35px;
        width: 35px;
        padding: 0 $default-padding;
      }
      .workout-date {
        font-size: 0.8em;
        font-weight: normal;
      }
      .workout-segment {
        font-weight: normal;
      }
      .workout-link {
        padding-left: $default-padding;
      }

      .fa {
        padding: 0 $default-padding * 0.3;
      }

      @media screen and (max-width: $small-limit) {
        .fa-trash,
        .fa-edit {
          border: solid 1px var(--card-border-color);
          border-radius: $border-radius;
          margin-left: $default-margin * 0.5;
          padding: 0 $default-padding;
        }
      }
    }
  }
</style>
