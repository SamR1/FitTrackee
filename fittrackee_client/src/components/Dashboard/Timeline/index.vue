<template>
  <div class="timeline">
    <WorkoutCard
      v-for="workout in workouts"
      :workout="workout"
      :sport="sports.filter((s) => s.id === workout.sport_id)[0]"
      :user="user"
      :key="workout.id"
    ></WorkoutCard>
  </div>
</template>

<script lang="ts">
  import {
    computed,
    ComputedRef,
    defineComponent,
    onBeforeMount,
    PropType,
  } from 'vue'

  import WorkoutCard from '@/components/Dashboard/Timeline/WorkoutCard.vue'
  import { SPORTS_STORE, WORKOUTS_STORE } from '@/store/constants'
  import { ISport } from '@/types/sports'
  import { IAuthUserProfile } from '@/types/user'
  import { IWorkout } from '@/types/workouts'
  import { useStore } from '@/use/useStore'

  export default defineComponent({
    name: 'Timeline',
    components: {
      WorkoutCard,
    },
    props: {
      user: {
        type: Object as PropType<IAuthUserProfile>,
        required: true,
      },
    },
    setup() {
      const store = useStore()
      onBeforeMount(() =>
        store.dispatch(WORKOUTS_STORE.ACTIONS.GET_USER_WORKOUTS, { page: 1 })
      )

      const workouts: ComputedRef<IWorkout[]> = computed(
        () => store.getters[WORKOUTS_STORE.GETTERS.USER_WORKOUTS]
      )

      const sports: ComputedRef<ISport[]> = computed(
        () => store.getters[SPORTS_STORE.GETTERS.SPORTS]
      )

      return { workouts, sports }
    },
  })
</script>
