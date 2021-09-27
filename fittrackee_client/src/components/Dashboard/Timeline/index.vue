<template>
  <div class="timeline">
    <div class="section-title">{{ t('workouts.LATEST_WORKOUTS') }}</div>
    <WorkoutCard
      v-for="index in [...Array(displayedWorkoutsCount).keys()]"
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
  </div>
</template>

<script lang="ts">
  import {
    ComputedRef,
    PropType,
    computed,
    defineComponent,
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

      const per_page = 5
      const displayedWorkoutsCount =
        props.user.nb_workouts >= per_page ? per_page : props.user.nb_workouts
      onBeforeMount(() =>
        store.dispatch(WORKOUTS_STORE.ACTIONS.GET_USER_WORKOUTS, {
          page: 1,
          per_page,
        })
      )

      const workouts: ComputedRef<IWorkout[]> = computed(
        () => store.getters[WORKOUTS_STORE.GETTERS.USER_WORKOUTS]
      )

      return { displayedWorkoutsCount, per_page, workouts, t }
    },
  })
</script>

<style lang="scss" scoped>
  @import '~@/scss/base';

  .no-workouts {
    margin-bottom: $default-margin * 2;
    padding: $default-padding;
  }
</style>
