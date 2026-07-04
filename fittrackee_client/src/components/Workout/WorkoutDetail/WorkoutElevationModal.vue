<template>
  <div id="modal" role="dialog" @click.self="emit('cancelAction')">
    <div class="custom-modal">
      <Card>
        <template #title>
          {{ $t('workouts.ELEVATION_DATA_SOURCE.MODAL_LABEL') }}
        </template>
        <template #content>
          <form class="change-elevation-source">
            <template v-if="elevationDataSourcesItems.length > 1">
              <div>
                {{ $t('workouts.ELEVATION_DATA_SOURCE.CHANGE_SOURCE') }}:
              </div>
              <label v-for="item in elevationDataSourcesItems" :key="item">
                <input
                  :id="item"
                  type="radio"
                  :name="item"
                  :checked="elevationDataSource === item"
                  @input="updateDatasource(item)"
                />
                {{ $t(`workouts.ELEVATION_DATA_SOURCE.${item}`) }}
              </label>
            </template>
            <div>{{ $t('workouts.ELEVATION_DATA_PROCESSING.LABEL') }}:</div>
            <label v-for="item in elevationProcessingItems" :key="item">
              <input
                :id="item"
                type="radio"
                :name="item"
                :checked="elevationProcessing == item"
                @input="updateProcessing(item)"
              />
              {{ $t(`workouts.ELEVATION_DATA_PROCESSING.${item}`) }}
            </label>
            <div class="elevation-loader">
              <div v-if="loading">
                <i class="fa fa-refresh fa-spin fa-fw"></i>
              </div>
            </div>
            <div class="modal-buttons">
              <button
                class="confirm"
                type="button"
                id="confirm-button"
                :disabled="loading"
                @click="confirmAction()"
              >
                {{ $t('buttons.SUBMIT') }}
              </button>
              <button
                class="cancel"
                type="button"
                id="cancel-button"
                :disabled="loading"
                @click="emit('cancelAction')"
              >
                {{ $t('buttons.CANCEL') }}
              </button>
            </div>
          </form>
        </template>
      </Card>
    </div>
  </div>
</template>

<script setup lang="ts">
  import {
    onUnmounted,
    onMounted,
    ref,
    toRefs,
    type ComputedRef,
    computed,
  } from 'vue'
  import type { Ref } from 'vue'

  import useApp from '@/composables/useApp'
  import { ROOT_STORE } from '@/store/constants.ts'
  import type {
    TElevationDataSource,
    TElevationProcessing,
  } from '@/types/user.ts'
  import type {
    IWorkoutElevationSourceDataPayload,
    IWorkoutObject,
  } from '@/types/workouts.ts'
  import { useStore } from '@/use/useStore.ts'

  interface Props {
    workoutObject: IWorkoutObject
    loading: boolean
  }
  const props = defineProps<Props>()
  const { loading, workoutObject } = toRefs(props)

  const store = useStore()

  const emit = defineEmits<{
    cancelAction: []
    confirmAction: [IWorkoutElevationSourceDataPayload]
  }>()

  const { elevationDataSourcesItems, elevationProcessingItems } = useApp()

  let cancelButton: HTMLElement | null = null
  let previousFocusedElement: HTMLInputElement | null = null

  const focusableElements: ComputedRef<string[]> = computed(() =>
    getFocusableElements()
  )

  const elevationDataSource: Ref<TElevationDataSource> = ref(
    workoutObject.value.elevationDataSource || 'file'
  )
  const elevationProcessing: Ref<TElevationProcessing> = ref(
    workoutObject.value.elevationProcessing || 'none'
  )

  function updateDatasource(value: TElevationDataSource) {
    elevationDataSource.value = value
  }
  function updateProcessing(value: TElevationProcessing) {
    elevationProcessing.value = value
  }
  function getFocusableElements() {
    const focusableElements = []
    elevationDataSourcesItems.value.forEach((item) =>
      focusableElements.push(item)
    )
    elevationProcessingItems.forEach((item) => focusableElements.push(item))
    focusableElements.push('confirm-button', 'cancel-button')
    return focusableElements
  }
  function focusTrap(e: KeyboardEvent) {
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
  function confirmAction() {
    emit('confirmAction', {
      workoutId: workoutObject.value.workoutId,
      elevationDataSource: elevationDataSource.value,
      elevationDataProcessing: elevationProcessing.value,
    })
  }

  onMounted(() => {
    store.commit(ROOT_STORE.MUTATIONS.EMPTY_ERROR_MESSAGES)
    previousFocusedElement = document.activeElement as HTMLInputElement | null
    cancelButton = document.getElementById('cancel-button')
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

          .change-elevation-source {
            display: flex;
            flex-direction: column;
            padding: $default-padding;
            gap: $default-padding * 0.5;
            label {
              font-weight: normal;
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

      .elevation-loader {
        height: 20px;
      }
    }
  }
</style>
