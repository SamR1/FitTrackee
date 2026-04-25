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
          @click="isEditing = true"
        >
          <i class="fa fa-edit" aria-hidden="true" />
        </button>
        <button
          v-if="isWorkoutOwner && !isEditing"
          class="transparent rounded-btn"
          id="delete-button"
          @click="isDeleting = true"
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
            name="media-description"
            :input="mediaAttachment.description || ''"
            :charLimit="1500"
            :rows="2"
            @updateValue="(e: ICustomTextareaData) => updateMediaDescription(e)"
          />
          <div class="buttons">
            <button class="cancel" @click="cancelEdition()">
              {{ $t('buttons.CANCEL') }}
            </button>
            <button
              class="confirm"
              :disabled="
                mediaLoading !== '' ||
                mediaAttachment.description === mediaDescription
              "
              @click="
                emit('updateDescriptionMedia', {
                  id: mediaAttachment.id,
                  description: mediaDescription,
                })
              "
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
              class="confirm danger"
              id="confirm-button"
              @click="emit('deleteMedia', mediaAttachment.id)"
            >
              {{ $t('common.YES') }}
            </button>
            <button
              tabindex="0"
              id="cancel-button"
              class="cancel"
              @click="isDeleting = false"
            >
              {{ $t('common.NO') }}
            </button>
          </div>
        </template>
      </div>
      <div v-else class="description">
        <div class="media-description-container bottom-border">
          <div class="media-description" v-if="mediaAttachment.description">
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
  import { computed, onUnmounted, onMounted, ref, toRefs, watch } from 'vue'
  import type { ComputedRef } from 'vue'

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

  const mediaAttachment: ComputedRef<IMediaAttachment | undefined> = computed(
    () => mediaAttachments.value[displayedMediaIndex.value]
  )
  const mediaLoading: ComputedRef<string> = computed(
    () => store.getters['WORKOUT_MEDIA_LOADING']
  )
  const focusableElements: ComputedRef<string[]> = computed(() => [
    ...(isWorkoutOwner.value ? ['edit-button', 'delete-button'] : []),
    'close-button',
    'prev-button',
    'next-button',
  ])

  function cancelEdition() {
    isEditing.value = false
    mediaDescription.value = ''
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
  function focusTrap(e: KeyboardEvent) {
    if (e.key === 'Escape' || e.keyCode === 27) {
      emit('closeModal')
      return
    }
    if (!document.activeElement?.id) {
      return
    }
    if (e.key === 'Tab' || e.keyCode === 9) {
      e.preventDefault()
      const elementIndex = focusableElements.value.indexOf(
        document.activeElement?.id
      )
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
