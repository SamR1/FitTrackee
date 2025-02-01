<template>
  <div class="appeal-action">
    <div class="suspended info-box">
      <i class="fa fa-info-circle" aria-hidden="true" />
      {{ $t('workouts.COMMENTS.SUSPENDED_COMMENT_BY_ADMIN') }}
      <button
        v-if="!success && !displayAppealForm && !hideSuspensionAppeal"
        class="transparent appeal-button"
        @click="displayAppealForm = `comment_${comment.id}`"
      >
        {{ $t('user.APPEAL') }}
      </button>
    </div>
    <ActionAppeal
      v-if="displayAppealForm"
      :report-action="action"
      :success="success === `comment_${comment.id}`"
      :loading="appealLoading === `comment_${comment.id}`"
      @submitForm="(text) => submitAppeal(text, 'comment', comment.id)"
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
  import { toRefs } from 'vue'

  import ActionAppeal from '@/components/Common/ActionAppeal.vue'
  import useAppeal from '@/composables/useAppeal'
  import type { IUserReportAction } from '@/types/user'
  import type { IComment } from '@/types/workouts'

  interface Props {
    action: IUserReportAction
    comment: IComment
    hideSuspensionAppeal?: boolean
  }
  const props = withDefaults(defineProps<Props>(), {
    hideSuspensionAppeal: false,
  })
  const { comment } = toRefs(props)

  const {
    appealLoading,
    displayAppealForm,
    success,
    submitAppeal,
    cancelAppeal,
  } = useAppeal()
</script>

<style scoped lang="scss">
  @use '~@/scss/vars.scss' as *;

  .notification-object {
    font-weight: bold;
    text-transform: capitalize;
  }
  .appeal-action {
    .appeal-button {
      padding: 0 $default-padding;
      font-size: 0.9em;
    }
  }
</style>
