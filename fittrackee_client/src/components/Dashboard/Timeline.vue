<template>
  <div id="timeline">
    <div class="section-title">{{ $t('workouts.LATEST_WORKOUTS') }}</div>
    <div v-if="user.nb_workouts > 0 && workouts.length === 0">
      <WorkoutCard
        v-for="index in [...Array(initWorkoutsCount).keys()]"
        :user="user"
        :useImperialUnits="user.imperial_units"
        :key="index"
      />
    </div>
    <div v-else>
      <WorkoutCard
        v-for="workout in workouts"
        :workout="workout"
        :sport="
          workouts.length > 0
            ? sports.filter((s) => s.id === workout.sport_id)[0]
            : null
        "
        :user="user"
        :useImperialUnits="user.imperial_units"
        :key="workout.id"
      />
      <NoWorkouts v-if="workouts.length === 0" />
      <div v-if="moreWorkoutsExist" class="more-workouts">
        <button @click="loadMoreWorkouts">
          {{ $t('workouts.LOAD_MORE_WORKOUT') }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
  import { ComputedRef, computed, ref, onBeforeMount, toRefs } from 'vue'

  import WorkoutCard from '@/components/Workout/WorkoutCard.vue'
  import NoWorkouts from '@/components/Workouts/NoWorkouts.vue'
  import { WORKOUTS_STORE } from '@/store/constants'
  import { ISport } from '@/types/sports'
  import { IUserProfile } from '@/types/user'
  import { IWorkout } from '@/types/workouts'
  import { useStore } from '@/use/useStore'
  import { defaultOrder } from '@/utils/workouts'

  interface Props {
    sports: ISport[]
    user: IUserProfile
  }
  const props = defineProps<Props>()

  const store = useStore()

  const { sports, user } = toRefs(props)
  const page = ref(1)
  const per_page = 5
  const initWorkoutsCount =
    props.user.nb_workouts >= per_page ? per_page : props.user.nb_workouts
  onBeforeMount(() => loadWorkouts())
  const workouts: ComputedRef<IWorkout[]> = computed(
    () => store.getters[WORKOUTS_STORE.GETTERS.TIMELINE_WORKOUTS]
  )
  const moreWorkoutsExist: ComputedRef<boolean> = computed(() =>
    workouts.value.length > 0
      ? workouts.value[workouts.value.length - 1].previous_workout !== null
      : false
  )

  function loadWorkouts() {
    store.dispatch(WORKOUTS_STORE.ACTIONS.GET_TIMELINE_WORKOUTS, {
      page: page.value,
      per_page,
      ...defaultOrder,
    })
  }
  function loadMoreWorkouts() {
    page.value += 1
    store.dispatch(WORKOUTS_STORE.ACTIONS.GET_MORE_TIMELINE_WORKOUTS, {
      page: page.value,
      per_page,
      ...defaultOrder,
    })
  }
</script>

<style lang="scss" scoped>
  #timeline {
    margin-bottom: 20px;

    .more-workouts {
      display: flex;
      justify-content: center;
    }
  }
</style>
