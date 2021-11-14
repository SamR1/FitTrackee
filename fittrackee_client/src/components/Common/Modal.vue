<template>
  <div id="modal">
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
          <ErrorMessage :message="errorMessages" v-if="errorMessages" />
          <div class="modal-buttons">
            <button
              class="confirm"
              v-if="!errorMessages"
              @click="emit('confirmAction')"
            >
              {{ $t('buttons.YES') }}
            </button>
            <button class="cancel" @click="emit('cancelAction')">
              {{ $t(`buttons.${errorMessages ? 'CANCEL' : 'NO'}`) }}
            </button>
          </div>
        </template>
      </Card>
    </div>
  </div>
</template>

<script setup lang="ts">
  import { ComputedRef, computed, toRefs, withDefaults, onUnmounted } from 'vue'

  import { ROOT_STORE } from '@/store/constants'
  import { useStore } from '@/use/useStore'

  interface Props {
    title: string
    message: string
    strongMessage?: string | null
  }
  const props = withDefaults(defineProps<Props>(), {
    strongMessage: () => null,
  })

  const emit = defineEmits(['cancelAction', 'confirmAction'])

  const store = useStore()

  const { title, message, strongMessage } = toRefs(props)
  const errorMessages: ComputedRef<string | string[] | null> = computed(
    () => store.getters[ROOT_STORE.GETTERS.ERROR_MESSAGES]
  )
  onUnmounted(() => store.commit(ROOT_STORE.MUTATIONS.EMPTY_ERROR_MESSAGES))
</script>

<style lang="scss" scoped>
  @import '~@/scss/base';
  #modal {
    position: fixed;
    top: 0;
    bottom: 0;
    left: 0;
    right: 0;
    background-color: var(--modal-background-color);
    padding: $default-padding;
    z-index: 1240;

    .custom-modal {
      background-color: var(--app-background-color);
      border-radius: $border-radius;
      max-width: 500px;
      margin: 25% auto;
      z-index: 1250;

      @media screen and (max-width: $medium-limit) {
        margin: 15% auto;
        width: 100%;
      }
      @media screen and (max-width: $small-limit) {
        margin: 50% 0;
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
        }
      }
    }
  }
</style>
