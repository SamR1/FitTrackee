<template>
  <div id="modal">
    <div class="custom-modal">
      <Card :without-title="false">
        <template #title>
          {{ title }}
        </template>
        <template #content>
          <div class="modal-message">{{ message }}</div>
          <ErrorMessage :message="errorMessages" v-if="errorMessages" />
          <div class="modal-buttons">
            <button class="confirm" @click="emit('confirmAction')">
              {{ t('buttons.YES') }}
            </button>
            <button class="cancel" @click="emit('cancelAction')">
              {{ t('buttons.NO') }}
            </button>
          </div>
        </template>
      </Card>
    </div>
  </div>
</template>

<script lang="ts">
  import { ComputedRef, computed, defineComponent, onUnmounted } from 'vue'
  import { useI18n } from 'vue-i18n'

  import Card from '@/components/Common/Card.vue'
  import ErrorMessage from '@/components/Common/ErrorMessage.vue'
  import { ROOT_STORE } from '@/store/constants'
  import { useStore } from '@/use/useStore'

  export default defineComponent({
    name: 'Modal',
    components: {
      Card,
      ErrorMessage,
    },
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
      const { t } = useI18n()
      const store = useStore()
      const errorMessages: ComputedRef<string | string[] | null> = computed(
        () => store.getters[ROOT_STORE.GETTERS.ERROR_MESSAGES]
      )
      onUnmounted(() => store.commit(ROOT_STORE.MUTATIONS.EMPTY_ERROR_MESSAGES))
      return { errorMessages, t, emit }
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

    @media screen and (max-width: $small-limit) {
      .custom-modal {
        margin: 20% 0;
        width: 100%;
      }
    }
  }
</style>
