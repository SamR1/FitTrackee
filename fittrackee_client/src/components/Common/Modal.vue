<template>
  <div id="modal">
    <div class="custom-modal">
      <Card>
        <template #title>
          {{ title }}
        </template>
        <template #content>
          <div class="modal-message">{{ message }}</div>
          <ErrorMessage :message="errorMessages" v-if="errorMessages" />
          <div class="modal-buttons">
            <button class="confirm" @click="emit('confirmAction')">
              {{ $t('buttons.YES') }}
            </button>
            <button class="cancel" @click="emit('cancelAction')">
              {{ $t('buttons.NO') }}
            </button>
          </div>
        </template>
      </Card>
    </div>
  </div>
</template>

<script lang="ts">
  import { ComputedRef, computed, defineComponent, onUnmounted } from 'vue'

  import { ROOT_STORE } from '@/store/constants'
  import { useStore } from '@/use/useStore'

  export default defineComponent({
    name: 'Modal',
    props: {
      title: {
        type: String,
        required: true,
      },
      message: {
        type: String,
        required: true,
      },
    },
    emits: ['cancelAction', 'confirmAction'],
    setup(props, { emit }) {
      const store = useStore()
      const errorMessages: ComputedRef<string | string[] | null> = computed(
        () => store.getters[ROOT_STORE.GETTERS.ERROR_MESSAGES]
      )
      onUnmounted(() => store.commit(ROOT_STORE.MUTATIONS.EMPTY_ERROR_MESSAGES))
      return { errorMessages, emit }
    },
  })
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
