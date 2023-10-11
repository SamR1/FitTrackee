<script setup lang="ts">
  import { computed, ComputedRef, Ref, ref, toRefs } from 'vue'

  import {
    REPORTS_STORE,
    ROOT_STORE,
    USERS_STORE,
    WORKOUTS_STORE,
  } from '@/store/constants'
  import { ICustomTextareaData } from '@/types/forms'
  import { useStore } from '@/use/useStore'

  interface Props {
    objectId: string
    objectType: string
  }
  const props = defineProps<Props>()
  const { objectId, objectType } = toRefs(props)

  const store = useStore()

  const labels: Record<string, string> = {
    comment: 'workouts.COMMENTS.REPORT',
    user: 'user.REPORT',
    workout: 'workouts.REPORT_WORKOUT',
  }
  const reportText: Ref<string> = ref('')
  const errorMessages: ComputedRef<string | string[] | null> = computed(
    () => store.getters[ROOT_STORE.GETTERS.ERROR_MESSAGES]
  )
  const reportStatus: ComputedRef<string | null> = computed(
    () => store.getters[REPORTS_STORE.GETTERS.REPORT_STATUS]
  )
  const label: ComputedRef<string> = computed(() => labels[objectType.value])

  function updateText(textareaData: ICustomTextareaData) {
    reportText.value = textareaData.value
  }
  function onCancel() {
    reportText.value = ''
    store.commit(ROOT_STORE.MUTATIONS.EMPTY_ERROR_MESSAGES)
    store.commit(REPORTS_STORE.MUTATIONS.SET_REPORT_STATUS, null)
    if (objectType.value === 'comment') {
      store.commit(WORKOUTS_STORE.MUTATIONS.SET_CURRENT_COMMENT_EDITION, {})
    } else if (objectType.value === 'workout') {
      store.commit(WORKOUTS_STORE.MUTATIONS.SET_CURRENT_REPORTING, false)
    } else {
      store.commit(USERS_STORE.MUTATIONS.UPDATE_USER_CURRENT_REPORTING, false)
    }
  }
  function submitReport() {
    store.dispatch(REPORTS_STORE.ACTIONS.SUBMIT_REPORT, {
      object_id: objectId.value,
      object_type: objectType.value,
      note: reportText.value,
    })
  }
</script>

<template>
  <div class="report-form">
    <form @submit.prevent="submitReport">
      <div class="form-items">
        <div class="form-item">
          <label for="report">
            {{ $t(label) }}
          </label>
          <CustomTextArea
            class="report-textarea"
            name="report"
            :required="true"
            :placeholder="$t('common.REPORT_PLACEHOLDER')"
            @updateValue="updateText"
          />
        </div>
      </div>
      <div class="form-select-buttons">
        <div class="spacer" />
        <div v-if="reportStatus === 'loading'">
          <Loader />
        </div>
        <div class="report-buttons" v-else>
          <button class="confirm" type="submit">
            {{ $t('buttons.SUBMIT') }}
          </button>
          <button class="cancel" @click.prevent="onCancel">
            {{ $t('buttons.CANCEL') }}
          </button>
        </div>
      </div>
      <ErrorMessage :message="errorMessages" v-if="errorMessages" />
    </form>
  </div>
</template>

<style scoped lang="scss">
  @import '~@/scss/vars.scss';

  .report-form {
    margin: $default-margin 0;
    .report-buttons {
      display: flex;
      gap: $default-padding;
    }
    .loader {
      border-width: 5px;
      height: 15px;
      margin: 0 10px;
      width: 15px;
    }
  }
</style>
