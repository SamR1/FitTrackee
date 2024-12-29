<template>
  <div id="timeline">
    <div class="section-title">{{ $t('workouts.LATEST_WORKOUTS') }}</div>
    <div v-if="authUser.nb_workouts > 0 && workouts.length === 0">
      <WorkoutCard
        v-for="index in [...Array(initWorkoutsCount).keys()]"
        :user="authUser"
        :useImperialUnits="authUser.imperial_units"
        :dateFormat="dateFormat"
        :timezone="authUser.timezone"
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
        :user="workout.user"
        :useImperialUnits="authUser.imperial_units"
        :dateFormat="dateFormat"
        :timezone="authUser.timezone"
        :key="workout.id"
      />
      <NoWorkouts v-if="workouts.length === 0" />
      <div v-if="pagination.has_next" class="more-workouts">
        <button @click="loadMoreWorkouts">
          {{ $t('workouts.LOAD_MORE_WORKOUT') }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
  import { computed, ref, onBeforeMount, toRefs, onUnmounted } from 'vue'
  import type { ComputedRef, Ref } from 'vue'

  import WorkoutCard from '@/components/Workout/WorkoutCard.vue'
  import NoWorkouts from '@/components/Workouts/NoWorkouts.vue'
  import useAuthUser from '@/composables/useAuthUser'
  import { AUTH_USER_STORE, WORKOUTS_STORE } from '@/store/constants'
  import type { IPagination } from '@/types/api.ts'
  import type { ISport } from '@/types/sports'
  import type { IAuthUserProfile } from '@/types/user'
  import type { IWorkout } from '@/types/workouts'
  import { useStore } from '@/use/useStore'
  import { defaultOrder } from '@/utils/workouts'

  interface Props {
    sports: ISport[]
    authUser: IAuthUserProfile
  }
  const props = defineProps<Props>()
  const { sports, authUser } = toRefs(props)

  const { dateFormat } = useAuthUser()

  const store = useStore()

  const per_page = 5

  const page: Ref<number> = ref(1)

  const initWorkoutsCount: ComputedRef<number> = computed(() =>
    authUser.value.nb_workouts >= per_page
      ? per_page
      : authUser.value.nb_workouts
  )
  const workouts: ComputedRef<IWorkout[]> = computed(
    () => store.getters[WORKOUTS_STORE.GETTERS.TIMELINE_WORKOUTS]
  )
  const pagination: ComputedRef<IPagination> = computed(
    () => store.getters[WORKOUTS_STORE.GETTERS.WORKOUTS_PAGINATION]
  )
  const isSuspended: ComputedRef<boolean> = computed(
    () => store.getters[AUTH_USER_STORE.GETTERS.IS_SUSPENDED]
  )

  function loadWorkouts() {
    if (!isSuspended.value) {
      store.dispatch(WORKOUTS_STORE.ACTIONS.GET_TIMELINE_WORKOUTS, {
        page: page.value,
        per_page,
        ...defaultOrder,
      })
    }
  }
  function loadMoreWorkouts() {
    if (!isSuspended.value) {
      page.value += 1
      store.dispatch(WORKOUTS_STORE.ACTIONS.GET_MORE_TIMELINE_WORKOUTS, {
        page: page.value,
        per_page,
        ...defaultOrder,
      })
    }
  }

  onBeforeMount(() => loadWorkouts())
  onUnmounted(() =>
    store.commit(
      WORKOUTS_STORE.MUTATIONS.SET_WORKOUTS_PAGINATION,
      {} as IPagination
    )
  )
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
