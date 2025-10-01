<template>
  <LPopup>
    <router-link
      class="workout-link"
      :to="{
        name: 'Workout',
        params: { workoutId: workout.id },
      }"
    >
      <SportImage :sport-label="sport" :color="color" />
      <span class="title">{{ workout.title }}</span>
      <VisibilityIcon :visibility="workout.workout_visibility" />
    </router-link>
  </LPopup>
</template>

<script lang="ts" setup>
  import { LPopup } from '@vue-leaflet/vue-leaflet'
  import { toRefs } from 'vue'

  import type { IMapWorkout } from '@/types/workouts.ts'

  interface Props {
    workout: IMapWorkout
    sport: string
    color: string | null
  }
  const props = defineProps<Props>()
  const { color, sport, workout } = toRefs(props)
</script>

<style lang="scss">
  @use '~@/scss/vars.scss' as *;

  .workout-link {
    display: flex;
    gap: $default-padding * 0.5;
    .title,
    .visibility {
      color: var(--app-a-color);
      filter: var(--map-filter);
    }

    .sport-img {
      height: 20px;
      width: 20px;
    }
  }
</style>
