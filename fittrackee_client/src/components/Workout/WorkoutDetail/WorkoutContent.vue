<template>
  <div id="workout-content">
    <Card>
      <template #title>
        {{ $t(`workouts.${contentType}`) }}
        <button
          class="transparent icon-button"
          :aria-label="$t(`buttons.EDIT`)"
          @click="editContent"
        >
          <i v-if="!isEdition" class="fa fa-edit" aria-hidden="true" />
        </button>
      </template>
      <template #content>
        <template v-if="isEdition">
          <form @submit.prevent="updateWorkoutContent">
            <label :for="contentType.toLowerCase()" class="visually-hidden">
              {{ $t(`workouts.${contentType}`) }}
            </label>
            <CustomTextArea
              :name="contentType.toLowerCase()"
              :input="content"
              :disabled="loading"
              :charLimit="contentType === 'NOTES' ? 500 : 10000"
              :rows="contentType === 'NOTES' ? 2 : 5"
              @updateValue="updateContent"
            />
            <div class="form-buttons">
              <button class="confirm" type="submit" :disabled="loading">
                {{ $t('buttons.SUBMIT') }}
              </button>
              <button class="cancel" @click.prevent="onCancel">
                {{ $t('buttons.CANCEL') }}
              </button>
              <div class="edition-loading" v-if="loading">
                <div>
                  <i class="fa fa-spinner fa-pulse" aria-hidden="true" />
                </div>
              </div>
            </div>
          </form>
        </template>
        <template v-else>
          <span
            class="workout-content"
            :class="{ notes: contentType === 'NOTES' || !content }"
            v-html="
              displayedContent && displayedContent !== ''
                ? linkifyAndClean(displayedContent)
                : $t(`workouts.NO_${contentType}`)
            "
          />
          <button
            class="read-more transparent"
            v-if="displayReadMoreButton"
            @click="readMore = !readMore"
          >
            <i
              :class="`fa fa-caret-${readMore ? 'up' : 'down'}`"
              aria-hidden="true"
            />
            {{ $t(`buttons.${readMore ? 'HIDE' : 'READ_MORE'}`) }}
          </button>
        </template>
        <ErrorMessage :message="errorMessages" v-if="errorMessages" />
      </template>
    </Card>
  </div>
</template>

<script setup lang="ts">
  import { computed, toRefs, ref, watch } from 'vue'
  import type { ComputedRef, Ref } from 'vue'

  import { ROOT_STORE, WORKOUTS_STORE } from '@/store/constants'
  import type { IEquipmentError } from '@/types/equipments'
  import type { IWorkoutContentEdition } from '@/types/workouts'
  import { useStore } from '@/use/useStore'
  import { linkifyAndClean } from '@/utils/inputs'

  interface Props {
    content?: string | null
    contentType: 'DESCRIPTION' | 'NOTES'
    workoutId: string
  }
  const props = withDefaults(defineProps<Props>(), {
    content: () => '',
  })

  const store = useStore()

  const { content, contentType, workoutId } = toRefs(props)

  const READ_MORE_LIMIT = 1000
  const displayReadMoreButton: ComputedRef<boolean> = computed(
    () => content.value !== null && content.value.length > READ_MORE_LIMIT
  )
  const workoutContentEdition: ComputedRef<IWorkoutContentEdition> = computed(
    () => store.getters[WORKOUTS_STORE.GETTERS.WORKOUT_CONTENT_EDITION]
  )
  const loading: ComputedRef<boolean> = computed(
    () =>
      workoutContentEdition.value.loading &&
      workoutContentEdition.value.contentType === contentType.value
  )
  const readMore: Ref<boolean> = ref(false)
  const displayedContent: ComputedRef<string | null> = computed(() =>
    readMore.value ? content.value : getTruncatedText(content.value)
  )
  const isEdition: Ref<boolean> = ref(false)
  const editedContent: Ref<string> = ref('')
  const errorMessages: ComputedRef<string | string[] | IEquipmentError | null> =
    computed(() =>
      workoutContentEdition.value.contentType === contentType.value
        ? store.getters[ROOT_STORE.GETTERS.ERROR_MESSAGES]
        : null
    )

  function getTruncatedText(text: string | null) {
    if (text === null || text.length <= READ_MORE_LIMIT) {
      return text
    }
    return text.slice(0, READ_MORE_LIMIT - 10) + '…'
  }
  function editContent() {
    store.commit(ROOT_STORE.MUTATIONS.EMPTY_ERROR_MESSAGES)
    isEdition.value = true
    editedContent.value = content.value ? content.value : ''
  }
  function updateContent(text: string) {
    editedContent.value = text
  }
  function onCancel() {
    isEdition.value = false
    editedContent.value = content.value ? content.value : ''
  }
  function updateWorkoutContent() {
    store.dispatch(WORKOUTS_STORE.ACTIONS.EDIT_WORKOUT_CONTENT, {
      workoutId: workoutId.value,
      content: editedContent.value,
      contentType: contentType.value,
    })
  }

  watch(
    () => loading.value,
    (newValue) => {
      if (!newValue) {
        isEdition.value = false
      }
    }
  )
</script>

<style lang="scss" scoped>
  @import '~@/scss/vars.scss';

  #workout-content {
    ::v-deep(.card-title) {
      text-transform: capitalize;
      .icon-button {
        cursor: pointer;
        padding: 0;
        margin-left: $default-margin * 0.5;
      }
    }
    ::v-deep(.card-content) {
      .workout-content {
        white-space: pre-wrap;
      }
      .read-more {
        font-size: 0.85em;
        font-weight: bold;
        padding: 0 10px;
      }
      .edition-loading {
        display: flex;
        align-items: center;
      }
      .notes {
        font-style: italic;
      }
      .error-message {
        margin: $default-margin 0;
      }
      .form-buttons {
        display: flex;
        margin-top: $default-margin * 0.5;
        gap: $default-padding;
      }
    }
  }
</style>
