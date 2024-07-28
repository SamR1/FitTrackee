<template>
  <div v-if="adminAction.id" class="appeal description-list">
    <dl v-if="adminAction.reason">
      <dt>{{ $t(`user.${actionTitle}_REASON`) }}:</dt>
      <dd>{{ adminAction.reason }}</dd>
    </dl>
    <div v-if="success || adminAction.appeal" class="appeal-submitted">
      <div
        class="info-box"
        :class="{ 'success-message': success, 'appeal-success': success }"
      >
        <span>
          <i class="fa fa-info-circle" aria-hidden="true" />
          {{ $t(`user.APPEAL_${success ? 'SUBMITTED' : 'IN_PROGRESS'}`) }}
          <button
            v-if="!success"
            class="transparent hide-button"
            @click="emit('hideMessage')"
          >
            {{ $t('common.HIDE') }}
          </button>
        </span>
      </div>
      <div v-if="adminAction.action_type.startsWith('user_')">
        <slot name="cancelButton"></slot>
      </div>
    </div>
    <form v-else @submit.prevent="submit">
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

  import { ROOT_STORE, WORKOUTS_STORE } from '@/store/constants'
  import type { IEquipmentError } from '@/types/equipments'
  import type { ICustomTextareaData } from '@/types/forms'
  import type { IUserAdminAction } from '@/types/user'
  import { useStore } from '@/use/useStore'

  interface Props {
    adminAction: IUserAdminAction
    loading: boolean
    success: boolean
  }
  const props = defineProps<Props>()

  const { adminAction, loading, success } = toRefs(props)

  const store = useStore()

  const errorMessages: ComputedRef<string | string[] | IEquipmentError | null> =
    computed(() => store.getters[ROOT_STORE.GETTERS.ERROR_MESSAGES])
  const appealText: Ref<string> = ref('')
  const actionTitle: ComputedRef<string> = computed(() =>
    adminAction.value.action_type.includes('_suspension')
      ? 'SUSPENSION'
      : 'WARNING'
  )

  const emit = defineEmits(['submitForm', 'hideMessage'])

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

  .report-buttons {
    display: flex;
    gap: $default-padding;
  }
  .hide-button {
    font-style: italic;
    padding: 0 $default-padding;
  }
</style>
