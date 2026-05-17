<template>
  <div id="modal" role="dialog" @click.self="emit('closeModal')">
    <div class="navigation-button navigation-button-prev">
      <button
        class="transparent rounded-btn"
        id="prev-button"
        :disabled="displayedMediaIndex === 0"
        @click="navigate('displayPreviousMedia')"
        :title="$t('workouts.PREVIOUS_PHOTO')"
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
          :title="$t('buttons.EDIT')"
        >
          <i class="fa fa-edit" aria-hidden="true" />
        </button>
        <button
          v-if="isWorkoutOwner && !isEditing"
          class="transparent rounded-btn"
          id="delete-button"
          @click="enableDeletion()"
          :title="$t('buttons.DELETE')"
        >
          <i class="fa fa-trash" aria-hidden="true" />
        </button>
        <button
          class="transparent rounded-btn"
          id="close-button"
          @click="emit('closeModal')"
          :title="$t('buttons.CLOSE')"
        >
          <i class="fa fa-close" aria-hidden="true" />
        </button>
      </div>
      <div class="modal-image">
        <img
          :class="{
            'with-edition': isDeleting || isEditing,
          }"
          :alt="mediaAttachment.description || ''"
          :src="mediaAttachment.url"
          :title="mediaAttachment.description"
          @touchstart.self.stop="handleSwipe"
        />
        <template v-if="mediaAttachment.description && !isEditing">
          <div
            class="modal-image-description white-space-pre-wrap"
            v-if="displayDescription"
          >
            {{ mediaAttachment.description }}
          </div>
          <button
            id="description-button"
            class="description-button"
            @click="displayDescription = !displayDescription"
            :title="
              $t(
                `workouts.${displayDescription ? 'HIDE' : 'DISPLAY'}_DESCRIPTION`
              )
            "
          >
            <i class="fa fa-info-circle" aria-hidden="true" />
          </button>
        </template>
      </div>
      <div v-if="isEditing || isDeleting" class="description-edition">
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
          <ErrorMessage :message="errorMessages" v-if="errorMessages" />
        </template>
      </div>
    </div>
    <div class="navigation-button navigation-button-next">
      <button
        class="transparent rounded-btn"
        id="next-button"
        :disabled="displayedMediaIndex === mediaAttachments.length - 1"
        @click="navigate('displayNextMedia')"
        :title="$t('workouts.NEXT_PHOTO')"
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
  const displayDescription = ref(false)
  const mediaDescription = ref('')
  const timer: Ref<ReturnType<typeof setTimeout> | undefined> = ref()
  const startPosition: Ref<number | undefined> = ref(undefined)

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
      focusableElements.push('description-button')
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

  function endSwipe(touchEvent: TouchEvent) {
    if (touchEvent.changedTouches.length !== 1 || !startPosition.value) {
      return
    }
    const endPosition = touchEvent.changedTouches[0].clientX
    if (displayedMediaIndex.value !== 0 && startPosition.value < endPosition) {
      navigate('displayPreviousMedia')
    } else if (
      displayedMediaIndex.value !== mediaAttachments.value.length - 1 &&
      startPosition.value > endPosition
    ) {
      navigate('displayNextMedia')
    }
  }
  function handleSwipe(touchEvent: TouchEvent) {
    if (touchEvent.changedTouches.length !== 1) {
      startPosition.value = undefined
      return
    }
    startPosition.value = touchEvent.changedTouches[0].clientX
    addEventListener('touchend', (touchEvent) => endSwipe(touchEvent), {
      once: true,
    })
  }

  watch(
    () => mediaAttachment.value,
    () => {
      mediaDescription.value = ''
      isDeleting.value = false
      displayDescription.value = false
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
    document.removeEventListener('touchend', endSwipe)
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

      .modal-image {
        position: relative;
        display: flex;
        img {
          border-radius: $border-radius;
          max-height: calc(100vh - 50px);
          object-fit: contain;
          &.with-edition {
            border-bottom-left-radius: initial;
            border-bottom-right-radius: initial;
            max-height: calc(100vh - 170px);
          }
        }
        .modal-image-description {
          position: absolute;
          background-color: var(--app-background-color);
          border-radius: $border-radius;
          padding: $default-padding;
          margin-right: $default-margin;
          bottom: 50px;
          left: $default-padding;
          max-height: 80%;
          overflow-y: auto;
        }
        .description-button {
          position: absolute;
          background: var(--button-transparent-hover-color);
          border-color: var(--button-transparent-hover-color);
          color: var(--button-hover-color);
          bottom: $default-padding;
          left: $default-padding;
          box-shadow: none;
          border-radius: 20%;
        }
      }

      .description-edition {
        padding: $default-padding;
        background-color: var(--app-background-color);
        border-bottom-left-radius: $border-radius;
        border-bottom-right-radius: $border-radius;

        .buttons {
          display: flex;
          gap: $default-padding;
          justify-content: flex-end;
        }
      }

      .deletion-confirmation {
        font-weight: bold;
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
