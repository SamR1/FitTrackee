<template>
  <div id="modal" role="dialog" @click.self="emit('closeModal')">
    <div class="navigation-button navigation-button-prev">
      <button
        class="transparent rounded-btn"
        id="prev-button"
        :disabled="displayedMediaIndex === 0"
        @click="navigate('displayPreviousMedia')"
      >
        <i class="fa fa-chevron-left" aria-hidden="true" />
      </button>
    </div>
    <div class="custom-gallery-modal" v-if="mediaAttachment?.id">
      <div class="top-bar">
        <button
          v-if="isWorkoutOwner && !isEditing"
          class="transparent rounded-btn"
          id="edit-button"
          @click="enableEdition()"
        >
          <i class="fa fa-edit" aria-hidden="true" />
        </button>
        <button
          v-if="isWorkoutOwner && !isEditing"
          class="transparent rounded-btn"
          id="delete-button"
          @click="enableDeletion()"
        >
          <i class="fa fa-trash" aria-hidden="true" />
        </button>
        <button
          class="transparent rounded-btn"
          id="close-button"
          @click="emit('closeModal')"
        >
          <i class="fa fa-close" aria-hidden="true" />
        </button>
      </div>
      <img
        :class="{
          'bottom-border':
            !mediaAttachment.description && !isDeleting && !isEditing,
        }"
        :alt="mediaAttachment.description || ''"
        :src="mediaAttachment.url"
      />
      <div
        v-if="isEditing || isDeleting"
        class="description-edition"
        :class="{
          'bottom-border':
            mediaAttachment.description || isDeleting || isEditing,
        }"
      >
        <template v-if="isEditing">
          <CustomTextArea
            name="media-description-textarea"
            :input="mediaAttachment.description || ''"
            :charLimit="1500"
            :rows="2"
            @updateValue="(e: ICustomTextareaData) => updateMediaDescription(e)"
          />
          <div class="buttons">
            <button id="cancel-edition" class="cancel" @click="cancelEdition()">
              {{ $t('buttons.CANCEL') }}
            </button>
            <button
              id="validate-edition"
              class="confirm"
              :disabled="
                mediaLoading !== '' ||
                mediaAttachment.description === mediaDescription
              "
              @click="validateEdition(mediaAttachment.id, mediaDescription)"
            >
              {{ $t('buttons.SAVE') }}
            </button>
          </div>
        </template>
        <template v-if="isDeleting">
          <div class="deletion-confirmation">
            {{ $t('workouts.PICTURE_DELETION_CONFIRMATION') }}
          </div>
          <div class="buttons">
            <button
              id="cancel-deletion"
              class="cancel"
              @click="isDeleting = false"
            >
              {{ $t('common.NO') }}
            </button>
            <button
              id="validate-deletion"
              class="confirm danger"
              @click="emit('deleteMedia', mediaAttachment.id)"
            >
              {{ $t('common.YES') }}
            </button>
          </div>
        </template>
      </div>
      <div v-else class="description">
        <div class="media-description-container bottom-border">
          <div
            id="media-description"
            class="media-description"
            v-if="mediaAttachment.description"
            tabindex="0"
          >
            {{ mediaAttachment.description }}
          </div>
          <ErrorMessage :message="errorMessages" v-if="errorMessages" />
        </div>
      </div>
    </div>
    <div class="navigation-button navigation-button-next">
      <button
        class="transparent rounded-btn"
        id="next-button"
        :disabled="displayedMediaIndex === mediaAttachments.length - 1"
        @click="navigate('displayNextMedia')"
      >
        <i class="fa fa-chevron-right" aria-hidden="true" />
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
  import {
    computed,
    nextTick,
    onUnmounted,
    onMounted,
    ref,
    toRefs,
    watch,
  } from 'vue'
  import type { ComputedRef, Ref } from 'vue'

  import useApp from '@/composables/useApp.ts'
  import type { ICustomTextareaData } from '@/types/forms.ts'
  import type { IMediaAttachment } from '@/types/workouts.ts'
  import { useStore } from '@/use/useStore.ts'

  interface Props {
    mediaAttachments: IMediaAttachment[]
    displayedMediaIndex: number
    isWorkoutOwner: boolean
  }
  const props = withDefaults(defineProps<Props>(), {})
  const { displayedMediaIndex, isWorkoutOwner, mediaAttachments } =
    toRefs(props)

  const emit = defineEmits<{
    closeModal: []
    displayNextMedia: []
    displayPreviousMedia: []
    deleteMedia: [string]
    updateDescriptionMedia: [
      {
        description: string
        id: string
      },
    ]
  }>()

  const { errorMessages } = useApp()

  const store = useStore()

  let previousFocusedElement: HTMLInputElement | null = null

  const isEditing = ref(false)
  const isDeleting = ref(false)
  const mediaDescription = ref('')
  const timer: Ref<ReturnType<typeof setTimeout> | undefined> = ref()

  const mediaAttachment: ComputedRef<IMediaAttachment | undefined> = computed(
    () => mediaAttachments.value[displayedMediaIndex.value]
  )
  const mediaLoading: ComputedRef<string> = computed(
    () => store.getters['WORKOUT_MEDIA_LOADING']
  )
  const focusableElements: ComputedRef<string[]> = computed(() =>
    getFocusableElements()
  )

  function cancelEdition() {
    isEditing.value = false
    mediaDescription.value = ''
    nextTick(() => {
      document.getElementById('edit-button')?.focus()
    })
  }
  function validateEdition(
    mediaAttachementId: string,
    mediaDescription: string
  ) {
    emit('updateDescriptionMedia', {
      id: mediaAttachementId,
      description: mediaDescription,
    })
    nextTick(() => {
      timer.value = setTimeout(() => {
        document.getElementById('edit-button')?.focus()
      }, 200)
    })
  }
  function updateMediaDescription(textareaData: ICustomTextareaData) {
    mediaDescription.value = textareaData.value
  }
  function navigate(event: 'displayNextMedia' | 'displayPreviousMedia') {
    isEditing.value = false
    // eslint-disable-next-line @typescript-eslint/ban-ts-comment
    // @ts-ignore
    emit(event)
  }
  function getFocusableElements() {
    const focusableElements = []
    if (isWorkoutOwner.value && !isEditing.value && !isDeleting.value) {
      focusableElements.push('edit-button', 'delete-button')
    }
    focusableElements.push('close-button')
    if (displayedMediaIndex.value !== 0) {
      focusableElements.push('prev-button')
    }
    if (displayedMediaIndex.value !== mediaAttachments.value.length - 1) {
      focusableElements.push('next-button')
    }
    if (mediaAttachment.value?.description && !isEditing.value) {
      focusableElements.push('media-description')
    }
    if (isEditing.value) {
      focusableElements.push(
        'media-description-textarea',
        'cancel-edition',
        'validate-edition'
      )
    }
    if (isDeleting.value) {
      focusableElements.push('cancel-deletion', 'validate-deletion')
    }
    return focusableElements
  }
  function focusTrap(e: KeyboardEvent) {
    if (e.key === 'Escape' || e.keyCode === 27) {
      emit('closeModal')
      return
    }

    if (e.key === 'ArrowLeft' || e.keyCode === 37) {
      document.getElementById('prev-button')?.click()
      return
    }

    if (e.key === 'ArrowRight' || e.keyCode === 39) {
      document.getElementById('next-button')?.click()
      return
    }

    let elementId = document.activeElement?.id
    if (!elementId) {
      elementId = focusableElements.value[0]
    }
    if (e.key === 'Tab' || e.keyCode === 9) {
      e.preventDefault()
      const elementIndex = focusableElements.value.indexOf(elementId)
      if (elementIndex === -1) {
        return
      }
      let elementToFocusId
      if (e.shiftKey) {
        elementToFocusId =
          elementIndex === 0
            ? focusableElements.value.length - 1
            : elementIndex - 1
      } else {
        elementToFocusId =
          elementIndex === focusableElements.value.length - 1
            ? 0
            : elementIndex + 1
      }
      document
        .getElementById(focusableElements.value[elementToFocusId])
        ?.focus()
    }
  }
  function enableEdition() {
    isEditing.value = true
    nextTick(() => {
      document.getElementById('media-description-textarea')?.focus()
    })
  }
  function enableDeletion() {
    isDeleting.value = true
    nextTick(() => {
      document.getElementById('cancel-deletion')?.focus()
    })
  }

  watch(
    () => mediaAttachment.value,
    () => {
      mediaDescription.value = ''
      isDeleting.value = false
    }
  )
  watch(
    () => mediaLoading.value,
    (newValue: string) => {
      if (newValue === '') {
        isEditing.value = false
      }
    }
  )

  onMounted(() => {
    previousFocusedElement = document.activeElement as HTMLInputElement | null
    document.getElementById(focusableElements.value[0])?.focus()
    document.addEventListener('keydown', focusTrap)
  })
  onUnmounted(() => {
    if (timer.value) {
      clearTimeout(timer.value)
    }
    document.removeEventListener('keydown', focusTrap)
    previousFocusedElement?.focus()
  })
</script>

<style lang="scss" scoped>
  @use '~@/scss/vars.scss' as *;
  #modal {
    position: fixed;
    padding: 0;
    top: 0;
    bottom: 0;
    left: 0;
    right: 0;
    background-color: var(--modal-background-color);
    z-index: 1240;
    display: flex;
    justify-content: center;
    align-items: center;
    overflow-y: scroll;

    @media screen and (max-width: $small-limit) {
      padding: 0;
    }

    .bottom-border {
      border-bottom-left-radius: $border-radius;
      border-bottom-right-radius: $border-radius;
    }

    .custom-gallery-modal {
      display: flex;
      flex-direction: column;
      justify-content: flex-start;
      border-radius: $border-radius;
      z-index: 1250;

      @media screen and (max-width: $medium-limit) {
        width: 100%;
      }

      .top-bar {
        display: flex;
        justify-content: flex-end;
      }

      img {
        border-top-left-radius: $border-radius;
        border-top-right-radius: $border-radius;
        max-height: calc(100vh - 160px);
        object-fit: contain;

        &.bottom-border {
          max-height: calc(100vh - 50px);
        }
      }

      .description-edition {
        padding: $default-padding;
        background-color: var(--app-background-color);

        .buttons {
          display: flex;
          gap: $default-padding;
          justify-content: flex-end;
        }
      }

      .deletion-confirmation {
        font-weight: bold;
      }

      .description {
        display: flex;
        align-items: center;

        .media-description-container {
          background-color: var(--app-background-color);
          display: flex;
          flex-direction: column;
          flex-grow: 1;

          .media-description {
            font-style: italic;
            text-align: center;
            white-space: pre-wrap;
            max-height: 90px;
            overflow-y: scroll;
            padding: $default-padding * 0.5 0;
            width: 100%;
          }
        }
      }
    }

    .navigation-button {
      display: flex;
      flex-grow: 1;

      &.navigation-button-next {
        justify-content: flex-end;
      }
    }

    .rounded-btn {
      color: var(--button-picture-navigation-color);
      border-radius: 50%;

      &:disabled {
        color: var(--button-picture-navigation-disabled-color);
      }

      &:not([disabled]):hover {
        background: var(--button-picture-navigation-hover-color);
      }
    }
  }
</style>
