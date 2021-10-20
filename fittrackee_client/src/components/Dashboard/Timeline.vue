<template>
  <div id="timeline">
    <div class="section-title">{{ $t('workouts.LATEST_WORKOUTS') }}</div>
    <div v-if="user.nb_workouts > 0 && workouts.length === 0">
      <WorkoutCard
        v-for="index in [...Array(initWorkoutsCount).keys()]"
        :user="user"
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

<script lang="ts">
  import {
    ComputedRef,
    PropType,
    computed,
    defineComponent,
    ref,
    onBeforeMount,
  } from 'vue'

  import WorkoutCard from '@/components/Workout/WorkoutCard.vue'
  import NoWorkouts from '@/components/Workouts/NoWorkouts.vue'
  import { WORKOUTS_STORE } from '@/store/constants'
  import { ISport } from '@/types/sports'
  import { IAuthUserProfile } from '@/types/user'
  import { IWorkout } from '@/types/workouts'
  import { useStore } from '@/use/useStore'

  export default defineComponent({
    name: 'Timeline',
    components: {
      NoWorkouts,
      WorkoutCard,
    },
    props: {
      sports: {
        type: Object as PropType<ISport[]>,
        required: true,
      },
      user: {
        type: Object as PropType<IAuthUserProfile>,
        required: true,
      },
    },
    setup(props) {
      const store = useStore()

      let page = ref(1)
      const per_page = 5
      const initWorkoutsCount =
        props.user.nb_workouts >= per_page ? per_page : props.user.nb_workouts
      onBeforeMount(() => loadWorkouts())

      const workouts: ComputedRef<IWorkout[]> = computed(
        () => store.getters[WORKOUTS_STORE.GETTERS.USER_WORKOUTS]
      )
      const moreWorkoutsExist: ComputedRef<boolean> = computed(() =>
        workouts.value.length > 0
          ? workouts.value[workouts.value.length - 1].previous_workout !== null
          : false
      )

      function loadWorkouts() {
        store.dispatch(WORKOUTS_STORE.ACTIONS.GET_USER_WORKOUTS, {
          page: page.value,
          per_page,
        })
      }
      function loadMoreWorkouts() {
        page.value += 1
        store.dispatch(WORKOUTS_STORE.ACTIONS.GET_MORE_USER_WORKOUTS, {
          page: page.value,
          per_page,
        })
      }

      return {
        initWorkoutsCount,
        moreWorkoutsExist,
        per_page,
        workouts,
        loadMoreWorkouts,
      }
    },
  })
</script>

<style lang="scss" scoped>
  @import '~@/scss/base';

  #timeline {
    margin-bottom: 20px;

    .more-workouts {
      display: flex;
      justify-content: center;
    }
  }
</style>
