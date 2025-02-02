<template>
  <div class="appeal box" :id="`appeal-${appeal.id}`">
    <div class="appeal-text">{{ appeal.text }}</div>
    <span
      class="appeal-date"
      :title="
        formatDate(appeal.created_at, authUser.timezone, authUser.date_format)
      "
    >
      {{
        formatDistance(new Date(appeal.created_at), new Date(), {
          addSuffix: true,
          locale,
        })
      }}
    </span>
    <template v-if="appeal.updated_at === null">
      <form
        v-if="appeal.approved === null"
        @submit.prevent="updateAppeal"
        class="appeal-actions"
      >
        <label for="appeal-reason" class="visually-hidden">
          {{ $t('administration.REASON') }}
        </label>
        <CustomTextArea
          name="appeal-reason"
          :required="true"
          :placeholder="
            $t('admin.APP_MODERATION.TEXTAREA_PLACEHOLDER.UPDATE_APPEAL')
          "
          @updateValue="updateReason"
        />
        <ErrorMessage
          v-if="errorMessages"
          :message="errorMessages"
          :no-margin="true"
        />
        <div class="appeal-actions-buttons">
          <button class="small approve" value="approve">
            {{ $t('buttons.APPROVE') }}
          </button>
          <button class="small reject" value="reject">
            {{ $t('buttons.REJECT') }}
          </button>
          <button class="small reject" type="button" @click="closeForm">
            {{ $t('buttons.CANCEL') }}
          </button>
        </div>
      </form>
    </template>
    <div v-else-if="appeal.approved === null" class="automatically-approved">
      {{
        $t('admin.APP_MODERATION.APPEAL.AUTOMATICALLY_APPROVED_BY_UNSUSPENSION')
      }}
    </div>
    <div class="description-list" v-else>
      <i18n-t
        :keypath="`admin.APP_MODERATION.APPEAL.${appeal.approved ? 'APPROVED' : 'REJECTED'}`"
        tag="p"
      >
        <span
          class="report-action-date"
          :title="
            formatDate(
              appeal.updated_at,
              authUser.timezone,
              authUser.date_format
            )
          "
        >
          {{
            formatDistance(new Date(appeal.updated_at), new Date(), {
              addSuffix: true,
              locale,
            })
          }}
        </span>
      </i18n-t>
      <dl>
        <dt>{{ $t('admin.APP_MODERATION.APPEAL.REASON_IS') }}</dt>
        <dd>{{ appeal.reason }}</dd>
      </dl>
    </div>
  </div>
</template>

<script setup lang="ts">
  import { formatDistance } from 'date-fns'
  import { ref, toRefs } from 'vue'
  import type { Ref } from 'vue'

  import CustomTextArea from '@/components/Common/CustomTextArea.vue'
  import useApp from '@/composables/useApp'
  import type { ICustomTextareaData } from '@/types/forms'
  import type { IReportActionAppeal, IAuthUserProfile } from '@/types/user'
  import { formatDate } from '@/utils/dates'

  interface Props {
    appeal: IReportActionAppeal
    authUser: IAuthUserProfile
  }
  const props = defineProps<Props>()
  const { appeal, authUser } = toRefs(props)

  const emit = defineEmits(['updateAppeal', 'closeAppeal'])

  const { errorMessages, locale } = useApp()

  const reason: Ref<string> = ref('')

  function updateAppeal(event: Event) {
    event.preventDefault()
    emit('updateAppeal', {
      approved:
        ((event as SubmitEvent).submitter as HTMLButtonElement).value ===
        'approve',
      appealId: appeal.value.id,
      reason: reason.value,
    })
  }
  function updateReason(textareaData: ICustomTextareaData) {
    reason.value = textareaData.value
  }
  function closeForm() {
    emit('closeAppeal')
  }
</script>

<style scoped lang="scss">
  @use '~@/scss/vars.scss' as *;
  .appeal {
    margin: $default-margin;
    color: var(--app-color);

    .appeal-date,
    .appeal-text {
      padding-left: $default-padding * 0.5;
    }
    .appeal-date {
      color: var(--app-color-light);
      font-size: 0.9em;
    }
    .appeal-text {
      font-style: normal;
    }

    .appeal-actions {
      display: flex;
      flex-direction: column;
      gap: 5px;
      margin: $default-padding * 0.5 0 0 $default-padding * 0.5;
      .appeal-actions-buttons {
        display: flex;
        gap: 5px;
      }
    }
    .automatically-approved {
      margin-top: $default-margin;
    }
    .description-list {
      dl {
        margin-bottom: -$default-margin;
      }
    }
  }
</style>
