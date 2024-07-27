<template>
  <div class="notification-object" v-if="displayObjectName">
    {{ $t('workouts.WORKOUT') }}:
  </div>
  <WorkoutCard
    :workout="workout"
    :sport="sport"
    :user="workout.user"
    :useImperialUnits="authUser.imperial_units"
    :dateFormat="dateFormat"
    :timezone="authUser.timezone"
  />
  <div v-if="displayAppeal" class="appeal-action">
    <button
      v-if="!success && !displayAppealForm"
      class="transparent appeal-button"
      @click="displayAppealForm = true"
    >
      {{ $t('user.APPEAL') }}
    </button>
    <ActionAppeal
      v-if="displayAppealForm"
      :admin-action="action"
      :success="success === `workout_${workout.id}`"
      :loading="appealLoading === `workout_${workout.id}`"
      @submitForm="submitAppeal"
      @hideMessage="displayAppealForm = false"
    >
      <template #cancelButton>
        <button @click="cancelAppeal()">
          {{ $t('buttons.CANCEL') }}
        </button>
      </template>
    </ActionAppeal>
  </div>
</template>

<script setup lang="ts">
  import { computed, ref, toRefs } from 'vue'
  import type { Ref, ComputedRef } from 'vue'

  import ActionAppeal from '@/components/Common/ActionAppeal.vue'
  import WorkoutCard from '@/components/Workout/WorkoutCard.vue'
  import {
    AUTH_USER_STORE,
    ROOT_STORE,
    SPORTS_STORE,
    WORKOUTS_STORE,
  } from '@/store/constants'
  import type { TLanguage } from '@/types/locales'
  import type { ISport } from '@/types/sports'
  import type { IAuthUserProfile, IUserAdminAction } from '@/types/user'
  import type { IWorkout } from '@/types/workouts'
  import { useStore } from '@/use/useStore'
  import { getDateFormat } from '@/utils/dates'

  interface Props {
    action: IUserAdminAction
    displayAppeal: boolean
    displayObjectName: boolean
    workout: IWorkout
  }
  const props = defineProps<Props>()
  const { action, displayAppeal, displayObjectName, workout } = toRefs(props)

  const store = useStore()

  const authUser: ComputedRef<IAuthUserProfile> = computed(
    () => store.getters[AUTH_USER_STORE.GETTERS.AUTH_USER_PROFILE]
  )
  const appLanguage: ComputedRef<TLanguage> = computed(
    () => store.getters[ROOT_STORE.GETTERS.LANGUAGE]
  )
  const sports: ComputedRef<ISport[]> = computed(
    () => store.getters[SPORTS_STORE.GETTERS.SPORTS]
  )
  const sport: ComputedRef<ISport | null> = computed(() => getSport())
  const dateFormat = computed(() =>
    getDateFormat(authUser.value.date_format, appLanguage.value)
  )
  const success: ComputedRef<null | string> = computed(
    () => store.getters[WORKOUTS_STORE.GETTERS.SUCCESS]
  )
  const appealLoading: ComputedRef<null | string> = computed(
    () => store.getters[WORKOUTS_STORE.GETTERS.APPEAL_LOADING]
  )
  const displayAppealForm: Ref<boolean> = ref(false)

  function getSport(): ISport | null {
    return workout.value
      ? sports.value.filter((s) => s.id === workout.value.sport_id)[0]
      : null
  }

  function submitAppeal(appealText: string) {
    store.dispatch(WORKOUTS_STORE.ACTIONS.MAKE_WORKOUT_APPEAL, {
      objectId: workout.value.id,
      text: appealText,
    })
  }
  function cancelAppeal() {
    displayAppealForm.value = false
    store.commit(ROOT_STORE.MUTATIONS.EMPTY_ERROR_MESSAGES)
  }
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
    .appeal {
      padding: 0 $default-padding;
    }

    .appeal-button {
      padding: 0 $default-padding;
      font-size: 0.9em;
    }
  }
</style>
