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
        <span id="photos">{{ $t('common.PHOTOS') }}</span>
        <button
          id="edit-button"
          class="transparent icon-button"
          v-if="isWorkoutOwner"
          @click="$router.push(`/workouts/${workoutId}/edit#media_visibility`)"
          :title="$t(`workouts.EDIT_WORKOUT`)"
        >
          <i class="fa fa-edit" aria-hidden="true" />
        </button>
      </template>
      <template #content>
        <div class="workout-media-gallery">
          <div
            v-for="(media, index) in mediaAttachments"
            :key="media.id"
            class="media-attachment"
            @click="setDisplayedMediaIndex(index)"
            @keydown.enter.prevent="setDisplayedMediaIndex(index)"
            role="button"
            tabindex="0"
            :title="media.description"
            :style="`background-image: url(${media.meta.thumbnail_url})`"
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

  import GalleryModal from '@/components/Workout/WorkoutDetail/GalleryModal.vue'
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

  #edit-button {
    margin-left: $default-margin;
  }

  ::v-deep(.card-content) {
    padding: $default-padding $default-padding * 1.4;

    .workout-media-gallery {
      display: flex;
      flex-wrap: wrap;
      gap: $default-padding;
      margin: 0;
      padding: 0;

      .media-attachment {
        cursor: pointer;
        background-size: cover;
        background-position: center;
        border-radius: 4px;
        padding: 5px;
        height: 200px;
        width: 23.3%;
        img {
          display: none;
        }
      }
    }
    @media screen and (max-width: $medium-limit) {
      .workout-media-gallery {
        .media-attachment {
          width: 31%;
        }
      }
    }
    @media screen and (max-width: 763px) {
      .workout-media-gallery {
        .media-attachment {
          width: 47.4%;
        }
      }
    }
    @media screen and (max-width: 626px) {
      .workout-media-gallery {
        .media-attachment {
          width: 47%;
        }
      }
    }
    @media screen and (max-width: $x-small-limit) {
      .workout-media-gallery {
        .media-attachment {
          width: 100%;
        }
      }
    }

    .media-visibility-level {
      font-size: 0.9em;
      font-style: italic;
      margin-top: $default-margin * 0.5;
      .visibility-label {
        color: var(--text-visibilty);
        text-transform: lowercase;
      }
    }
  }
</style>
