<template>
  <div v-if="suspension.id" class="appeal description-list">
    <dl v-if="suspension.reason">
      <dt>{{ $t('user.SUSPENSION_REASON') }}:</dt>
      <dd>{{ suspension.reason }}</dd>
    </dl>
    <div v-if="success || suspension.appeal" class="appeal-submitted">
      <div
        class="info-box"
        :class="{ 'success-message': success, 'appeal-success': success }"
      >
        <span>
          <i class="fa fa-info-circle" aria-hidden="true" />
          {{ $t(`user.APPEAL_${success ? 'SUBMITTED' : 'IN_PROGRESS'}`) }}
        </span>
      </div>
      <div v-if="suspension.action_type === 'user_suspension'">
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
        <div v-if="loading && appealText">
          <Loader />
        </div>
        <div class="report-buttons" v-else>
          <button class="confirm" type="submit" :disabled="!appealText">
            {{ $t('buttons.SUBMIT') }}
          </button>
          <slot name="cancelButton"></slot>
        </div>
      </div>
      <ErrorMessage :message="errorMessages" v-if="errorMessages" />
    </form>
  </div>
</template>

<script setup lang="ts">
  import { computed, ref, toRefs } from 'vue'
  import type { ComputedRef, Ref } from 'vue'

  import { ROOT_STORE } from '@/store/constants'
  import type { IEquipmentError } from '@/types/equipments'
  import type { ICustomTextareaData } from '@/types/forms'
  import type { ISuspension } from '@/types/user'
  import { useStore } from '@/use/useStore'

  interface Props {
    suspension: ISuspension
    loading: boolean
    success: boolean
  }
  const props = defineProps<Props>()

  const { loading, success } = toRefs(props)

  const store = useStore()

  const errorMessages: ComputedRef<string | string[] | IEquipmentError | null> =
    computed(() => store.getters[ROOT_STORE.GETTERS.ERROR_MESSAGES])
  const appealText: Ref<string> = ref('')

  const emit = defineEmits(['submitForm'])

  function updateText(textareaData: ICustomTextareaData) {
    appealText.value = textareaData.value
  }
  function submit() {
    emit('submitForm', appealText.value)
  }
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
</style>
