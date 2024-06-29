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
    <form
      v-if="appeal.approved === null"
      @submit.prevent="updateAppeal"
      class="appeal-actions"
    >
      <CustomTextArea
        name="appeal-reason"
        :required="true"
        :placeholder="
          $t('admin.APP_MODERATION.TEXTAREA_PLACEHOLDER.UPDATE_APPEAL')
        "
        @updateValue="updateReason"
      />
      <div class="appeal-actions-buttons">
        <button class="small approve" value="approve">
          {{ $t('buttons.APPROVE') }}
        </button>
        <button class="small reject" value="reject">
          {{ $t('buttons.REJECT') }}
        </button>
      </div>
    </form>
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
  import type { Locale } from 'date-fns'
  import { computed, ref, toRefs } from 'vue'
  import type { ComputedRef, Ref } from 'vue'

  import CustomTextArea from '@/components/Common/CustomTextArea.vue'
  import { ROOT_STORE } from '@/store/constants'
  import type { ICustomTextareaData } from '@/types/forms'
  import type { ISuspensionAppeal, IAuthUserProfile } from '@/types/user'
  import { useStore } from '@/use/useStore'
  import { formatDate } from '@/utils/dates'

  interface Props {
    appeal: ISuspensionAppeal
    authUser: IAuthUserProfile
  }

  const props = defineProps<Props>()
  const { appeal, authUser } = toRefs(props)

  const store = useStore()

  const emit = defineEmits(['updateAppeal'])

  const locale: ComputedRef<Locale> = computed(
    () => store.getters[ROOT_STORE.GETTERS.LOCALE]
  )
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
</script>

<style scoped lang="scss">
  @import '~@/scss/vars.scss';
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
  }
</style>
