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
    v-if="action && displayWorkoutAppeal"
    :action="action"
    :workout="workout"
    :display-suspension-message="action.action_type === 'workout_suspension'"
  />
  <AlertMessage
    message="workouts.SUSPENDED_BY_ADMIN"
    v-else-if="workout.suspension?.report_id"
  >
    <template
      #additionalMessage
      v-if="workout.suspension.report_id !== reportId"
    >
      <i18n-t keypath="common.SEE_REPORT" tag="span">
        <router-link :to="`/admin/reports/${workout.suspension.report_id}`">
          #{{ workout.suspension.report_id }}
        </router-link>
      </i18n-t>
    </template>
  </AlertMessage>
</template>

<script setup lang="ts">
  import { computed, toRefs } from 'vue'
  import type { ComputedRef } from 'vue'

  import WorkoutActionAppeal from '@/components/Workout/WorkoutActionAppeal.vue'
  import WorkoutCard from '@/components/Workout/WorkoutCard.vue'
  import useAuthUser from '@/composables/useAuthUser'
  import useSports from '@/composables/useSports'
  import type { ISport } from '@/types/sports'
  import type { IUserReportAction } from '@/types/user'
  import type { IWorkout } from '@/types/workouts'

  interface Props {
    action?: IUserReportAction | null
    displayAppeal: boolean
    displayObjectName: boolean
    workout: IWorkout
    reportId?: number
  }
  const props = withDefaults(defineProps<Props>(), {
    action: null,
  })
  const { action, displayAppeal, displayObjectName, reportId, workout } =
    toRefs(props)

  const { getWorkoutSport } = useSports()
  const { dateFormat, imperialUnits, timezone } = useAuthUser()

  const sport: ComputedRef<ISport | null> = computed(() =>
    getWorkoutSport(workout.value)
  )
  const displayWorkoutAppeal: ComputedRef<boolean> = computed(
    () =>
      workout.value.suspended === true &&
      action.value !== null &&
      (!action.value.appeal ||
        action.value.appeal?.approved === false ||
        (action.value.appeal?.approved === null &&
          !action.value.appeal?.updated_at)) &&
      displayAppeal.value
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

  .alert-message {
    margin: $default-margin 0;
  }
</style>
