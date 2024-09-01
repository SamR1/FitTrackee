<template>
  <div class="notification-object" v-if="displayObjectName">
    {{ $t('workouts.WORKOUT') }}:
  </div>
  <WorkoutCard
    :workout="workout"
    :sport="sport"
    :user="workout.user"
    :useImperialUnits="imperialUnits"
    :dateFormat="dateFormat"
    :timezone="timezone"
  />
  <WorkoutActionAppeal
    v-if="action && displayAppeal"
    :action="action"
    :workout="workout"
    display-suspension-message
  />
</template>

<script setup lang="ts">
  import { computed, toRefs } from 'vue'
  import type { ComputedRef } from 'vue'

  import WorkoutActionAppeal from '@/components/Workout/WorkoutActionAppeal.vue'
  import WorkoutCard from '@/components/Workout/WorkoutCard.vue'
  import useAuthUser from '@/composables/useAuthUser'
  import useSports from '@/composables/useSports'
  import type { ISport } from '@/types/sports'
  import type { IUserAdminAction } from '@/types/user'
  import type { IWorkout } from '@/types/workouts'

  interface Props {
    action?: IUserAdminAction
    displayAppeal: boolean
    displayObjectName: boolean
    workout: IWorkout
  }
  const props = defineProps<Props>()
  const { displayAppeal, displayObjectName, workout } = toRefs(props)

  const { getWorkoutSport } = useSports()
  const { dateFormat, imperialUnits, timezone } = useAuthUser()

  const sport: ComputedRef<ISport | null> = computed(() =>
    getWorkoutSport(workout.value)
  )
</script>

<style scoped lang="scss">
  @import '~@/scss/vars';

  .notification-object {
    font-weight: bold;
    text-transform: capitalize;
  }

  .workout-card {
    margin-bottom: 0;
  }

  .appeal-action {
    margin: 0 $default-margin;
  }
</style>
