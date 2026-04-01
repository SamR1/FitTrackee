<template>
  <div class="form-item">
    <label for="mediaAttachmentFile">
      {{ $t('common.PHOTOS') }} (<span> {{ mediaAttachments.length }}/20</span
      >):
    </label>
    <input
      ref="mediaAttachmentFile"
      id="mediaAttachmentFile"
      name="mediaAttachmentFile"
      type="file"
      :multiple="false"
      accept=".jpeg, .jpg, .gif, .png, .webp"
      :disabled="loading || mediaAttachments.length === 20"
      @change="uploadMediaAttachment"
    />
  </div>
  <div class="loading-media">
    <i
      v-if="mediaLoading === 'new'"
      class="fa fa-refresh fa-spin"
      aria-hidden="true"
    />
    {{ ' ' }}
    <span v-if="mediaLoading === 'new'">{{ $t('common.LOADING') }}</span>
  </div>
  <div class="media-attachments">
    <div
      v-for="media in mediaAttachments"
      :key="media.id"
      class="media-attachment"
    >
      <div class="media-img" :style="`background-image: url(${media.url})`">
        <img :alt="media.description || ''" :src="media.url" />
      </div>
      <div class="media-alt">
        <label :for="`media-description-${media.id}`">
          {{ $t('workouts.DESCRIPTION') }}:
          <CustomTextArea
            :name="`media-description-${media.id}`"
            :input="media.description || ''"
            :disabled="loading"
            :charLimit="1500"
            :rows="2"
            @updateValue="
              (e: ICustomTextareaData) => updateMediaDescription(e, media.id)
            "
          />
        </label>
        <div class="description-buttons">
          <div class="loading-media" v-if="mediaLoading === media.id">
            <i class="fa fa-refresh fa-spin" aria-hidden="true" />{{ ' ' }}
            <span>{{ $t('common.LOADING') }}</span>
          </div>
          <button
            class="danger"
            @click.prevent="deleteMediaAttachment(media.id)"
            :disabled="loading"
          >
            {{ $t('buttons.DELETE') }}
          </button>
          <button
            class="confirm"
            @click.prevent="saveMediaDescription(media.id)"
            :disabled="
              loading ||
              !(media.id in mediaDescriptions) ||
              media.description === mediaDescriptions[media.id]
            "
          >
            {{ $t('buttons.SAVE') }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
  import { computed, onBeforeMount, onUnmounted, ref, toRefs, watch } from 'vue'
  import type { ComputedRef, Ref } from 'vue'

  import { WORKOUTS_STORE } from '@/store/constants.ts'
  import type { ICustomTextareaData } from '@/types/forms.ts'
  import type { IMediaAttachment } from '@/types/workouts'
  import { useStore } from '@/use/useStore.ts'

  interface Props {
    loading: boolean
    workoutMediaAttachments: IMediaAttachment[]
  }
  const props = defineProps<Props>()
  const { loading, workoutMediaAttachments } = toRefs(props)

  const store = useStore()

  const mediaLoading: ComputedRef<string> = computed(
    () => store.getters['WORKOUT_MEDIA_LOADING']
  )
  const mediaAttachments: ComputedRef<IMediaAttachment[]> = computed(
    () => store.getters['WORKOUT_MEDIA_ATTACHMENTS']
  )
  const mediaDescriptions: Ref<Record<string, string>> = ref({})
  const mediaAttachmentFile: Ref<HTMLInputElement | undefined> = ref(undefined)

  async function uploadMediaAttachment(event: Event) {
    const files = (event.target as HTMLInputElement).files || []
    if (files.length > 0) {
      for (const file of files) {
        store.dispatch(WORKOUTS_STORE.ACTIONS.ADD_WORKOUT_MEDIA_ATTACHMENT, {
          file,
        })
      }
    }
  }
  function updateMediaDescription(
    textareaData: ICustomTextareaData,
    mediaAttachmentId: string
  ) {
    mediaDescriptions.value[mediaAttachmentId] = textareaData.value
  }
  function saveMediaDescription(mediaAttachmentId: string) {
    store.dispatch(WORKOUTS_STORE.ACTIONS.UPDATE_WORKOUT_MEDIA_ATTACHMENT, {
      id: mediaAttachmentId,
      description: mediaDescriptions.value[mediaAttachmentId],
    })
  }
  function deleteMediaAttachment(mediaAttachmentId: string) {
    store.dispatch(WORKOUTS_STORE.ACTIONS.DELETE_WORKOUT_MEDIA_ATTACHMENT, {
      id: mediaAttachmentId,
    })
  }

  watch(
    () => mediaLoading.value,
    (newValue: string, oldValue: string) => {
      if (newValue === '' && oldValue === 'new' && mediaAttachmentFile.value) {
        mediaAttachmentFile.value.value = ''
      }
    }
  )

  onBeforeMount(() => {
    store.commit(
      WORKOUTS_STORE.MUTATIONS.SET_WORKOUT_MEDIA_ATTACHMENTS,
      workoutMediaAttachments.value
    )
  })
  onUnmounted(() =>
    store.commit(WORKOUTS_STORE.MUTATIONS.EMPTY_WORKOUT_MEDIA_ATTACHMENTS)
  )
</script>

<style scoped lang="scss">
  @use '~@/scss/vars.scss' as *;
  .media-attachments {
    display: flex;
    flex-direction: column;
    padding: $default-padding;
    .media-attachment {
      padding: $default-padding 0;
      display: flex;
      flex-direction: row;
      gap: $default-padding;
      .media-img {
        background-size: cover;
        background-position: center;
        border-radius: 4px;
        height: 100px;
        padding: 5px;
        width: 300px;
        img {
          display: none;
        }
      }
      .media-alt {
        display: flex;
        flex-direction: column;
        width: 100%;
        .description-buttons {
          display: flex;
          gap: $default-padding;
          justify-content: flex-end;
          align-items: center;
        }
      }
    }
  }
  .loading-media {
    height: 10px;
    font-style: italic;
    font-size: 0.85em;
    padding-left: $default-padding * 2;
    align-items: center;
  }
</style>
