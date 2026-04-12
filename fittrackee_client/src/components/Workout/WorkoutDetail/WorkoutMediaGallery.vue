<template>
  <div id="workout-media">
    <GalleryModal
      v-if="displayedMediaIndex !== undefined"
      :media-attachments="mediaAttachments"
      :displayed-media-index="displayedMediaIndex"
      :is-workout-owner="isWorkoutOwner"
      @closeModal="setDisplayedMediaIndex(undefined)"
      @deleteMedia="deleteMediaAttachment"
      @displayPreviousMedia="updateMediaIndex('prev')"
      @displayNextMedia="updateMediaIndex('next')"
      @updateDescriptionMedia="updateMediaDescription"
    />
    <Card>
      <template #title>
        {{ $t('common.PHOTOS') }}
      </template>
      <template #content>
        <div class="workout-media-gallery">
          <div
            v-for="(media, index) in mediaAttachments"
            :key="media.id"
            class="media-attachment"
            @click="setDisplayedMediaIndex(index)"
            @keydown.enter="setDisplayedMediaIndex(index)"
            role="button"
            tabindex="0"
            :title="media.description"
          >
            <img :alt="media.description" :src="media.meta.thumbnail_url" />
          </div>
        </div>
        <div class="media-visibility-level">
          {{ $t('visibility_levels.VISIBILITY') }}:
          <VisibilityIcon
            v-if="mediaVisibility"
            :visibility="mediaVisibility"
          />
          <span class="visibility-label">
            ({{ $t(`visibility_levels.LEVELS.${mediaVisibility}`) }})
          </span>
        </div>
        <ErrorMessage :message="errorMessages" v-if="errorMessages" />
      </template>
    </Card>
  </div>
</template>

<script setup lang="ts">
  import { computed, toRefs } from 'vue'
  import type { ComputedRef } from 'vue'

  import GalleryModal from '@/components/Common/GalleryModal.vue'
  import useApp from '@/composables/useApp.ts'
  import { WORKOUTS_STORE } from '@/store/constants.ts'
  import type { TVisibilityLevels } from '@/types/user.ts'
  import type { IMediaAttachment } from '@/types/workouts.ts'
  import { useStore } from '@/use/useStore.ts'

  interface Props {
    mediaAttachments: IMediaAttachment[]
    mediaVisibility: TVisibilityLevels | undefined
    isWorkoutOwner: boolean
    workoutId: string
  }
  const props = defineProps<Props>()
  const { isWorkoutOwner, mediaAttachments, mediaVisibility, workoutId } =
    toRefs(props)

  const store = useStore()

  const { errorMessages } = useApp()

  const displayedMediaIndex: ComputedRef<number | undefined> = computed(
    () => store.getters[WORKOUTS_STORE.GETTERS.DISPLAYED_MEDIA_INDEX]
  )

  function setDisplayedMediaIndex(index: number | undefined) {
    store.commit(WORKOUTS_STORE.MUTATIONS.SET_DISPLAYED_MEDIA_INDEX, index)
  }
  function updateMediaIndex(value: 'prev' | 'next') {
    if (displayedMediaIndex.value === undefined) {
      return
    }
    if (value === 'prev' && displayedMediaIndex.value > 0) {
      setDisplayedMediaIndex(displayedMediaIndex.value - 1)
    }
    if (
      value === 'next' &&
      displayedMediaIndex.value < mediaAttachments.value.length - 1
    ) {
      setDisplayedMediaIndex(displayedMediaIndex.value + 1)
    }
  }
  function deleteMediaAttachment(mediaAttachmentId: string) {
    store.dispatch(WORKOUTS_STORE.ACTIONS.DELETE_WORKOUT_MEDIA_ATTACHMENT, {
      id: mediaAttachmentId,
      workoutId: workoutId.value,
    })
    setDisplayedMediaIndex(undefined)
  }
  function updateMediaDescription(payload: {
    description: string
    id: string
  }) {
    store.dispatch(WORKOUTS_STORE.ACTIONS.UPDATE_WORKOUT_MEDIA_ATTACHMENT, {
      id: payload.id,
      description: payload.description,
      workoutId: workoutId.value,
    })
  }
</script>

<style scoped lang="scss">
  @use '~@/scss/vars.scss' as *;

  .workout-media-gallery {
    columns: auto 4;
    column-gap: $default-padding;
    margin: 0;
    padding: 0;

    .media-attachment {
      break-inside: avoid;
      display: inline-block;
      cursor: pointer;

      img {
        display: block;
        border-radius: 5px;
        height: auto;
        width: 100%;
        margin-bottom: $default-padding * 0.5;
      }
    }
  }
  .media-visibility-level {
    font-size: 0.9em;
    font-style: italic;
    .visibility-label {
      color: var(--text-visibilty);
      text-transform: lowercase;
    }
  }
  @media screen and (max-width: $medium-limit) {
    .workout-media-gallery {
      columns: auto 3;
    }
  }
  @media screen and (max-width: $small-limit) {
    .workout-media-gallery {
      columns: auto 2;
    }
  }
  @media screen and (max-width: $x-small-limit) {
    .workout-media-gallery {
      columns: auto 1;
    }
  }
</style>
