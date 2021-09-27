<template>
  <div id="timeline">
    <div class="section-title">{{ t('workouts.LATEST_WORKOUTS') }}</div>
    <WorkoutCard
      v-for="index in [...Array(workoutsToDisplayCount()).keys()]"
      :workout="workouts.length > 0 ? workouts[index] : null"
      :sport="
        workouts.length > 0
          ? sports.filter((s) => s.id === workouts[index].sport_id)[0]
          : null
      "
      :user="user"
      :key="index"
    />
    <div v-if="workouts.length === 0" class="no-workouts">
      {{ t('workouts.NO_WORKOUTS') }}
    </div>
    <div v-if="moreWorkoutsExist" class="more-workouts">
      <button @click="loadMoreWorkouts">
        {{ t('workouts.LOAD_MORE_WORKOUT') }}
      </button>
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
  import { useI18n } from 'vue-i18n'

  import WorkoutCard from '@/components/Dashboard/Timeline/WorkoutCard.vue'
  import { WORKOUTS_STORE } from '@/store/constants'
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
      const { t } = useI18n()

      let page = ref(1)
      const per_page = 5
      onBeforeMount(() => loadWorkouts())

      const initWorkoutsCount =
        props.user.nb_workouts >= per_page ? per_page : props.user.nb_workouts

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
        loadWorkouts()
      }
      function workoutsToDisplayCount() {
        return workouts.value.length > initWorkoutsCount
          ? workouts.value.length
          : initWorkoutsCount
      }

      return {
        initWorkoutsCount,
        moreWorkoutsExist,
        per_page,
        workouts,
        t,
        loadMoreWorkouts,
        workoutsToDisplayCount,
      }
    },
  })
</script>

<style lang="scss" scoped>
  @import '~@/scss/base';

  #timeline {
    margin-bottom: 20px;
    .no-workouts {
      margin-bottom: $default-margin * 2;
      padding: $default-padding;
    }
    .more-workouts {
      display: flex;
      justify-content: center;
    }
  }
</style>
