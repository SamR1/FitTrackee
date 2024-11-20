<template>
  <div v-if="reportAction.id" class="appeal description-list">
    <dl v-if="reportAction.reason">
      <dt>{{ $t(`user.${actionTitle}_REASON`) }}:</dt>
      <dd>{{ reportAction.reason }}</dd>
    </dl>
    <div v-if="success || reportAction.appeal" class="appeal-submitted">
      <div
        class="info-box"
        :class="{
          'success-message': success,
          'appeal-success': success,
          'appeal-approved': appealStatus === 'APPROVED',
          'appeal-rejected': appealStatus === 'REJECTED',
        }"
      >
        <span>
          <i
            class="fa"
            :class="{
              'fa-info-circle': appealStatus !== 'REJECTED',
              'fa-times': appealStatus === 'REJECTED',
            }"
            aria-hidden="true"
          />
          {{ $t(`user.APPEAL_${appealStatus}`) }}
          <button
            v-if="displayHideButton"
            class="transparent hide-button"
            @click="emit('hideMessage')"
          >
            {{ $t('common.HIDE') }}
          </button>
        </span>
      </div>
      <div>
        <slot name="additionalButtons"></slot>
      </div>
    </div>
    <form v-else-if="canAppeal" @submit.prevent="submit">
      <div class="form-items">
        <div class="form-item">
          <label for="appeal">{{ $t('user.APPEAL') }}:</label>
          <CustomTextArea
            name="appeal"
            :required="true"
            @updateValue="updateText"
          />
          <div class="info-box appeal-info">
            <span>
              <i class="fa fa-info-circle" aria-hidden="true" />
              {{ $t('user.YOU_CAN_APPEAL_ONCE') }}
            </span>
          </div>
        </div>
      </div>
      <div class="form-select-buttons">
        <div class="report-buttons">
          <button class="confirm" type="submit" :disabled="!appealText">
            {{ $t('buttons.SUBMIT') }}
          </button>
          <slot name="cancelButton"></slot>
          <div class="action-loading">
            <i
              v-if="loading && appealText"
              class="fa fa-spinner fa-pulse"
              aria-hidden="true"
            />
          </div>
        </div>
      </div>
      <ErrorMessage :message="errorMessages" v-if="errorMessages" />
    </form>
  </div>
</template>

<script setup lang="ts">
  import { computed, onUnmounted, ref, toRefs } from 'vue'
  import type { ComputedRef, Ref } from 'vue'
  import { useRoute } from 'vue-router'

  import { ROOT_STORE, WORKOUTS_STORE } from '@/store/constants'
  import type { IEquipmentError } from '@/types/equipments'
  import type { ICustomTextareaData } from '@/types/forms'
  import type { IUserReportAction } from '@/types/user'
  import { useStore } from '@/use/useStore'

  interface Props {
    reportAction: IUserReportAction
    loading: boolean
    success: boolean
    canAppeal?: boolean
  }
  const props = withDefaults(defineProps<Props>(), {
    canAppeal: true,
  })

  const { reportAction, loading, success } = toRefs(props)

  const route = useRoute()
  const store = useStore()

  const errorMessages: ComputedRef<string | string[] | IEquipmentError | null> =
    computed(() => store.getters[ROOT_STORE.GETTERS.ERROR_MESSAGES])
  const appealText: Ref<string> = ref('')
  const actionTitle: ComputedRef<string> = computed(() =>
    reportAction.value.action_type.includes('_suspension')
      ? 'SUSPENSION'
      : 'WARNING'
  )
  const appealStatus: ComputedRef<string> = computed(() => getAppealStatus())
  const displayHideButton: ComputedRef<boolean> = computed(
    () =>
      !success.value &&
      !['AuthUserAccountSuspension', 'UserSanctionDetail'].includes(
        route.name as string
      )
  )

  const emit = defineEmits(['submitForm', 'hideMessage'])

  function getAppealStatus() {
    if (success.value) {
      return 'SUBMITTED'
    }
    const appeal = reportAction.value.appeal
    if (appeal?.approved === false) {
      return 'REJECTED'
    } else if (appeal?.approved === true) {
      return 'APPROVED'
    }
    return 'IN_PROGRESS'
  }
  function updateText(textareaData: ICustomTextareaData) {
    appealText.value = textareaData.value
  }
  function submit() {
    emit('submitForm', appealText.value)
  }

  onUnmounted(() => {
    store.commit(WORKOUTS_STORE.MUTATIONS.SET_APPEAL_LOADING, null)
    store.commit(WORKOUTS_STORE.MUTATIONS.SET_SUCCESS, null)
  })
</script>

<style scoped lang="scss">
  @import '~@/scss/vars';
  .description-list {
    margin-bottom: $default-margin;
    dl {
      margin-bottom: 0;
    }
  }

  .error-message,
  .appeal-info {
    margin: $default-margin 0;
  }

  .appeal-submitted {
    display: flex;
    flex-direction: column;
    gap: $default-padding;
    .appeal-success {
      margin: $default-margin 0 0;
    }
  }
  .appeal-approved {
    background: var(--success-background-color);
    color: var(--success-color);
    button {
      color: var(--success-color);
    }
  }
  .appeal-rejected {
    background: var(--error-background-color);
    color: var(--error-color);
    button {
      color: var(--error-color);
    }
  }

  .report-buttons {
    display: flex;
    gap: $default-padding;
  }
  .hide-button {
    font-style: italic;
    padding: 0 $default-padding;
  }
</style>
