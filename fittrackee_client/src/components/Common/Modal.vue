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
              @click="emit('confirmAction')"
            >
              {{ $t('buttons.YES') }}
            </button>
            <button
              tabindex="0"
              id="cancel-button"
              class="cancel"
              @click="emit('cancelAction')"
            >
              {{ $t(`buttons.${errorMessages ? 'CANCEL' : 'NO'}`) }}
            </button>
          </div>
        </template>
      </Card>
    </div>
  </div>
</template>

<script setup lang="ts">
  import { onUnmounted, onMounted, toRefs } from 'vue'

  import useApp from '@/composables/useApp'

  interface Props {
    title: string
    message: string
    strongMessage?: string | null
    loading?: boolean
    warning?: string
    hideErrorMessage?: boolean
  }
  const props = withDefaults(defineProps<Props>(), {
    loading: false,
    strongMessage: () => '',
    warning: () => '',
    hideErrorMessage: false,
  })
  const { title, message, strongMessage } = toRefs(props)

  const emit = defineEmits(['cancelAction', 'confirmAction'])

  const { errorMessages } = useApp()

  let confirmButton: HTMLElement | null = null
  let cancelButton: HTMLElement | null = null
  let previousFocusedElement: HTMLInputElement | null = null

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

  onMounted(() => {
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
