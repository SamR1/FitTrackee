<template>
  <div id="modal" role="dialog" @click.self="emit('cancelAction')">
    <div class="custom-modal">
      <Card>
        <template #title>
          {{ title }}
        </template>
        <template #content>
          <div class="modal-message" v-if="strongMessage">
            <i18n-t :keypath="message">
              <span>{{ strongMessage }}</span>
            </i18n-t>
          </div>
          <div class="modal-message" v-else>{{ message }}</div>
          <div class="info-box" v-if="warning">
            <i class="fa fa-exclamation-triangle" aria-hidden="true" />
            {{ warning }}
          </div>
          <div v-if="additionalActionText" class="additional-action">
            <label>
              <input type="checkbox" v-model="checked" />
              {{ additionalActionText }}
            </label>
          </div>
          <ErrorMessage
            :message="errorMessages"
            v-if="errorMessages && !hideErrorMessage"
          />
          <div v-if="loading">
            <Loader />
          </div>
          <div class="modal-buttons" v-else>
            <button
              class="confirm"
              :class="{ danger: warning }"
              id="confirm-button"
              v-if="!errorMessages"
              @click="confirmAction()"
            >
              {{ $t('common.YES') }}
            </button>
            <button
              tabindex="0"
              id="cancel-button"
              class="cancel"
              @click="emit('cancelAction')"
            >
              {{ $t(errorMessages ? 'buttons.CANCEL' : 'common.NO') }}
            </button>
          </div>
        </template>
      </Card>
    </div>
  </div>
</template>

<script setup lang="ts">
  import { onUnmounted, onMounted, ref, toRefs } from 'vue'
  import type { Ref } from 'vue'

  import useApp from '@/composables/useApp'
  import { ROOT_STORE } from '@/store/constants.ts'
  import { useStore } from '@/use/useStore.ts'

  interface Props {
    title: string
    message: string
    strongMessage?: string | null
    loading?: boolean
    warning?: string
    hideErrorMessage?: boolean
    additionalActionText?: string
  }
  const props = withDefaults(defineProps<Props>(), {
    loading: false,
    strongMessage: '',
    warning: '',
    hideErrorMessage: false,
    additionalActionText: '',
  })
  const { additionalActionText, title, message, strongMessage } = toRefs(props)

  const store = useStore()

  const emit = defineEmits<{
    cancelAction: []
    confirmAction: [additionalAction?: boolean]
  }>()
  const { errorMessages } = useApp()

  let confirmButton: HTMLElement | null = null
  let cancelButton: HTMLElement | null = null
  let previousFocusedElement: HTMLInputElement | null = null
  const checked: Ref<boolean> = ref(false)

  function focusTrap(e: KeyboardEvent) {
    if (e.key === 'Tab' || e.keyCode === 9) {
      e.preventDefault()
      if (document.activeElement?.id === 'cancel-button') {
        confirmButton?.focus()
      } else {
        cancelButton?.focus()
      }
    }
  }
  function confirmAction() {
    if (additionalActionText.value) {
      emit('confirmAction', checked.value)
    } else {
      emit('confirmAction')
    }
  }

  onMounted(() => {
    store.commit(ROOT_STORE.MUTATIONS.EMPTY_ERROR_MESSAGES)
    previousFocusedElement = document.activeElement as HTMLInputElement | null
    cancelButton = document.getElementById('cancel-button')
    confirmButton = document.getElementById('confirm-button')
    if (cancelButton) {
      cancelButton.focus()
    }
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

    .custom-modal {
      background-color: var(--app-background-color);
      border-radius: $border-radius;
      max-width: 500px;
      z-index: 1250;

      @media screen and (max-width: $medium-limit) {
        width: 100%;
      }

      ::v-deep(.card) {
        border: 0;
        margin: 0;

        .card-content {
          display: flex;
          flex-direction: column;

          .modal-message {
            padding: $default-padding;
            span {
              font-weight: bold;
            }
          }

          .modal-buttons {
            display: flex;
            justify-content: flex-end;

            button {
              margin: $default-padding * 0.5;
            }
          }

          .info-box {
            margin: 0 $default-margin $default-margin;
          }

          .additional-action {
            label {
              padding-left: $default-padding * 0.5;
              font-weight: normal;
              font-style: italic;
            }
          }
        }
      }
      .loader {
        border-width: 5px;
        height: 20px;
        margin-left: 45%;
        width: 20px;
      }
    }
  }
</style>
