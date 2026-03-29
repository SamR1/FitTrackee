<template>
  <div id="modal" role="dialog" @click.self="emit('closeModal')">
    <div class="custom-gallery-modal" v-if="mediaAttachment?.id">
      <div class="top-bar">
        <button
          v-if="isWorkoutOwner && !isEditing"
          class="transparent"
          id="edit-button"
          @click="isEditing = true"
        >
          <i class="fa fa-edit" aria-hidden="true" />
        </button>
        <button
          v-if="isWorkoutOwner"
          class="transparent"
          id="delete-button"
          @click="emit('deleteMedia', mediaAttachment.id)"
        >
          <i class="fa fa-trash" aria-hidden="true" />
        </button>
        <button
          class="transparent"
          id="close-button"
          @click="emit('closeModal')"
        >
          <i class="fa fa-close" aria-hidden="true" />
        </button>
      </div>
      <img
        :alt="mediaAttachment.description || ''"
        :src="mediaAttachment.url"
      />
      <div class="navigation-bar">
        <button
          class="transparent"
          id="prev-button"
          :disabled="displayedMediaIndex === 0"
          @click="emit('displayPreviousMedia')"
        >
          <i class="fa fa-chevron-left" aria-hidden="true" />
        </button>
        <div class="media-description">
          <div v-if="isEditing" class="description-edition">
            <CustomTextArea
              name="media-description"
              :input="mediaAttachment.description || ''"
              :charLimit="1500"
              :rows="2"
              @updateValue="
                (e: ICustomTextareaData) => updateMediaDescription(e)
              "
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
          </div>
          <span v-else>
            {{
              mediaAttachment.description
                ? mediaAttachment.description
                : $t('common.NO_DESCRIPTION')
            }}
          </span>
          <ErrorMessage :message="errorMessages" v-if="errorMessages" />
        </div>
        <button
          class="transparent"
          id="next-button"
          :disabled="displayedMediaIndex === mediaAttachments.length - 1"
          @click="emit('displayNextMedia')"
        >
          <i class="fa fa-chevron-right" aria-hidden="true" />
        </button>
      </div>
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
    top: 0;
    bottom: 0;
    left: 0;
    right: 0;
    background-color: var(--modal-background-color);
    padding: $default-padding;
    z-index: 1240;
    display: flex;
    justify-content: center;
    align-items: center;

    .custom-gallery-modal {
      display: flex;
      flex-direction: column;
      background-color: var(--app-background-color);
      border-radius: $border-radius;
      max-width: 90%;
      z-index: 1250;

      @media screen and (max-width: $medium-limit) {
        width: 100%;
      }

      .top-bar {
        display: flex;
        justify-content: flex-end;
      }

      img {
        max-height: calc(100vh - 80px);
      }

      .navigation-bar {
        display: flex;
        align-items: center;

        .description-edition {
          display: flex;
          flex-direction: column;
          padding: $default-padding 0;

          .buttons {
            display: flex;
            gap: $default-padding;
            justify-content: flex-end;
          }
        }

        .media-description {
          flex-grow: 1;
          font-style: italic;
          text-align: center;
          white-space: pre-wrap;
        }
      }
    }
  }
</style>
