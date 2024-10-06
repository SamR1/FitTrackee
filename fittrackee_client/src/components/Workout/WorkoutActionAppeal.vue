<template>
  <div class="appeal-action">
    <div
      :class="{
        suspended: displaySuspensionMessage,
        'info-box': displaySuspensionMessage,
      }"
    >
      <template v-if="displaySuspensionMessage">
        <i class="fa fa-info-circle" aria-hidden="true" />
        {{ $t('workouts.SUSPENDED_BY_ADMIN') }}
      </template>
      <button
        v-if="displaySuspensionMessage && !success && !displayAppealForm"
        class="transparent appeal-button"
        @click="displayAppealForm = objectTypeId"
      >
        {{ $t('user.APPEAL') }}
      </button>
    </div>
    <ActionAppeal
      v-if="displayAppealForm"
      :report-action="action"
      :success="success === objectTypeId"
      :loading="appealLoading === objectTypeId"
      @submitForm="(text) => submitAppeal(text, 'workout', workout.id)"
      @hideMessage="displayAppealForm = null"
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
  import { computed, toRefs } from 'vue'
  import type { ComputedRef } from 'vue'

  import ActionAppeal from '@/components/Common/ActionAppeal.vue'
  import useAppeal from '@/composables/useAppeal'
  import type { IUserReportAction } from '@/types/user'
  import type { IWorkout } from '@/types/workouts'

  interface Props {
    action: IUserReportAction
    workout: IWorkout
    displaySuspensionMessage?: boolean
  }
  const props = withDefaults(defineProps<Props>(), {
    displaySuspensionMessage: false,
  })
  const { workout } = toRefs(props)

  const {
    appealLoading,
    displayAppealForm,
    success,
    submitAppeal,
    cancelAppeal,
  } = useAppeal()

  const objectTypeId: ComputedRef<string> = computed(
    () => `workout_${workout.value.id}`
  )
</script>

<style lang="scss" scoped>
  @import '~@/scss/vars';

  .appeal-action {
    .appeal-button {
      padding: 0 $default-padding;
      font-size: 0.9em;
    }
  }

  .suspended {
    font-size: 0.9em;
  }
</style>
