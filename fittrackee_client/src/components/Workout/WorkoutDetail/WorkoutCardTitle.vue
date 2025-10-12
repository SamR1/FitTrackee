<template>
  <div id="workout-card-title">
    <button
      v-if="isWorkoutOwner || workoutObject.segmentId !== null"
      class="workout-previous workout-arrow transparent"
      :class="{ inactive: !workoutObject.previousUrl }"
      :disabled="!workoutObject.previousUrl || refreshLoading"
      :title="
        workoutObject.previousUrl
          ? $t(`workouts.PREVIOUS_${workoutObject.type}`)
          : $t(`workouts.NO_PREVIOUS_${workoutObject.type}`)
      "
      @click="
        workoutObject.previousUrl
          ? $router.push(workoutObject.previousUrl)
          : null
      "
    >
      <i class="fa fa-chevron-left" aria-hidden="true" />
    </button>
    <div class="workout-card-title">
      <SportImage :sport-label="sport.label" :color="sport.color" />
      <div
        class="workout-title-date"
        v-if="isWorkoutOwner || !workoutObject.suspended"
      >
        <div class="workout-title" v-if="workoutObject.type === 'WORKOUT'">
          <span>{{ workoutObject.title }}</span>
          <div v-if="isAuthenticated" class="workout-buttons">
            <button
              class="transparent icon-button likes"
              :disabled="refreshLoading"
              @click="updateLike(workoutObject)"
              :title="
                $t(
                  `workouts.${workoutObject.liked ? 'REMOVE_LIKE' : 'LIKE_WORKOUT'}`
                )
              "
              :aria-label="`${$t(`workouts.${workoutObject.liked ? 'REMOVE_LIKE' : 'LIKE_WORKOUT'}`)} (${workoutObject.likes_count} ${$t(
                'workouts.LIKES',
                workoutObject.likes_count
              )})`"
            >
              <i
                class="fa"
                :class="{
                  'fa-heart': workoutObject.likes_count > 0,
                  'fa-heart-o': workoutObject.likes_count === 0,
                  liked: workoutObject.liked,
                }"
                aria-hidden="true"
              />
            </button>
            <router-link
              :to="`/workouts/${workoutObject.workoutId}/likes`"
              v-if="workoutObject.likes_count > 0"
              class="likes-count"
            >
              {{ workoutObject.likes_count }}
            </router-link>
            <button
              class="transparent icon-button"
              :disabled="refreshLoading"
              v-if="isWorkoutOwner"
              @click="
                $router.push({
                  name: 'EditWorkout',
                  params: { workoutId: workoutObject.workoutId },
                })
              "
              :title="$t(`workouts.EDIT_WORKOUT`)"
            >
              <i class="fa fa-edit" aria-hidden="true" />
            </button>
            <div class="download-files">
              <button
                id="download-workout"
                v-if="isWorkoutOwner && workoutObject.with_gpx"
                class="transparent icon-button"
                :disabled="refreshLoading"
                @click.prevent="toggleDownloadButtons()"
                :title="$t(`workouts.DOWNLOAD_WORKOUT`)"
              >
                <i
                  class="fa fa-download"
                  aria-hidden="true"
                  id="download-workout-icon"
                />
              </button>
              <div
                class="download-files-buttons"
                v-if="displayDownloadButtons && isWorkoutOwner"
                v-click-outside="hideDownloadButtons"
              >
                <button
                  class="transparent icon-button"
                  :disabled="refreshLoading"
                  @click.prevent="downloadWorkoutFile(workoutObject.workoutId)"
                  :title="
                    workoutObject.originalFile === 'gpx'
                      ? $t(`workouts.DOWNLOAD_ORIGINAL_FILE`, {
                          fileExtension: workoutObject.originalFile,
                        })
                      : $t(`workouts.DOWNLOAD_GPX_FILE`)
                  "
                >
                  <i class="fa fa-download" aria-hidden="true" />
                  .gpx
                </button>
                <button
                  class="transparent icon-button"
                  :disabled="refreshLoading"
                  @click.prevent="
                    downloadWorkoutFile(workoutObject.workoutId, {
                      original: true,
                    })
                  "
                  :title="
                    $t(`workouts.DOWNLOAD_ORIGINAL_FILE`, {
                      fileExtension: workoutObject.originalFile,
                    })
                  "
                  v-if="workoutObject.originalFile != 'gpx'"
                >
                  <i class="fa fa-download" aria-hidden="true" />
                  .{{ workoutObject.originalFile }}
                </button>
              </div>
            </div>
            <button
              v-if="workoutObject.with_gpx && isWorkoutOwner"
              class="transparent icon-button"
              :disabled="refreshLoading"
              @click.prevent="refreshGpx(workoutObject.workoutId)"
              :title="$t(`workouts.REFRESH_WORKOUT`)"
            >
              <i
                class="fa fa-refresh"
                :class="{ 'fa-spin': refreshLoading }"
                aria-hidden="true"
              />
            </button>
            <button
              v-if="isWorkoutOwner"
              id="delete-workout-button"
              class="transparent icon-button"
              :disabled="refreshLoading"
              @click.prevent="displayDeleteModal"
              :title="$t(`workouts.DELETE_WORKOUT`)"
            >
              <i class="fa fa-trash" aria-hidden="true" />
            </button>
            <button
              v-if="
                !isWorkoutOwner &&
                !currentlyReporting &&
                reportStatus !== `workout-${workoutObject.workoutId}-created`
              "
              class="transparent icon-button"
              :disabled="refreshLoading"
              @click.prevent="displayReportForm"
              :title="$t('workouts.REPORT_WORKOUT')"
            >
              <i class="fa fa-flag" aria-hidden="true" />
            </button>
          </div>
          <div
            v-else
            :title="`${workoutObject.likes_count} ${$t(
              'workouts.LIKES',
              workoutObject.likes_count
            )}`"
          >
            <i
              class="fa"
              :class="{
                'fa-heart': workoutObject.likes_count > 0,
                'fa-heart-o': workoutObject.likes_count === 0,
                liked: workoutObject.liked,
              }"
            />
            <router-link
              :to="`/workouts/${workoutObject.workoutId}/likes`"
              v-if="workoutObject.likes_count > 0"
              class="likes-count"
            >
              {{ workoutObject.likes_count }}
            </router-link>
          </div>
          <div v-if="refreshLoading" class="refresh-message">
            {{ $t('workouts.REFRESHING_WORKOUT') }}
          </div>
        </div>
        <div class="workout-title" v-else-if="workoutObject.segmentId !== null">
          {{ workoutObject.title }}
          <span class="workout-segment">
            —
            <i class="fa fa-map-marker" aria-hidden="true" />
            {{ $t('workouts.SEGMENT') }}
            {{ workoutObject.segmentId + 1 }}
          </span>
        </div>
        <div class="workout-date">
          <time :datetime="workoutObject.workoutFullDate">
            {{ workoutObject.workoutDate }} - {{ workoutObject.workoutTime }}
          </time>
          <span class="workout-link">
            <router-link
              v-if="workoutObject.type === 'SEGMENT'"
              :to="{
                name: 'Workout',
                params: { workoutId: workoutObject.workoutId },
              }"
            >
              > {{ $t('workouts.BACK_TO_WORKOUT') }}
            </router-link>
          </span>
        </div>
      </div>
    </div>
    <button
      v-if="isWorkoutOwner || workoutObject.segmentId !== null"
      class="workout-next workout-arrow transparent"
      :class="{ inactive: !workoutObject.nextUrl }"
      :disabled="!workoutObject.nextUrl || refreshLoading"
      :title="
        workoutObject.nextUrl
          ? $t(`workouts.NEXT_${workoutObject.type}`)
          : $t(`workouts.NO_NEXT_${workoutObject.type}`)
      "
      @click="
        workoutObject.nextUrl ? $router.push(workoutObject.nextUrl) : null
      "
    >
      <i class="fa fa-chevron-right" aria-hidden="true" />
    </button>
  </div>
</template>

<script setup lang="ts">
  import { computed, ref, toRefs, watch } from 'vue'
  import type { ComputedRef, Ref } from 'vue'

  import authApi from '@/api/authApi'
  import useAuthUser from '@/composables/useAuthUser'
  import { REPORTS_STORE, WORKOUTS_STORE } from '@/store/constants'
  import type { ISport } from '@/types/sports'
  import type { IWorkoutObject } from '@/types/workouts'
  import { useStore } from '@/use/useStore'

  interface Props {
    sport: ISport
    workoutObject: IWorkoutObject
    isWorkoutOwner: boolean
    refreshLoading: boolean
  }
  const props = defineProps<Props>()
  const { isWorkoutOwner, refreshLoading, sport, workoutObject } = toRefs(props)

  const emit = defineEmits(['displayModal'])

  const store = useStore()

  const { isAuthenticated } = useAuthUser()

  const workoutFileMimetypes = {
    fit: 'application/vnd.ant.fit',
    gpx: 'application/gpx+xml',
    kml: 'application/vnd.google-earth.kml+xml',
    tcx: 'application/vnd.garmin.tcx+xml',
  }
  const currentlyReporting: ComputedRef<boolean> = computed(
    () => store.getters[WORKOUTS_STORE.GETTERS.CURRENT_REPORTING]
  )
  const reportStatus: ComputedRef<string | null> = computed(
    () => store.getters[REPORTS_STORE.GETTERS.REPORT_STATUS]
  )
  const displayDownloadButtons: Ref<boolean> = ref(false)

  async function downloadWorkoutFile(
    workoutId: string,
    options: { original?: boolean } = {}
  ) {
    const fileExtension =
      options.original && workoutObject.value.originalFile
        ? workoutObject.value.originalFile
        : 'gpx'
    const mimeType = workoutFileMimetypes[fileExtension]
    await authApi
      .get(
        `workouts/${workoutId}/${options.original ? 'original' : 'gpx'}/download`,
        {
          responseType: 'blob',
        }
      )
      .then((response) => {
        const gpxFileUrl = window.URL.createObjectURL(
          new Blob([response.data], { type: mimeType })
        )
        const gpxLink = document.createElement('a')
        gpxLink.href = gpxFileUrl
        gpxLink.setAttribute('download', `${workoutId}.${fileExtension}`)
        document.body.appendChild(gpxLink)
        gpxLink.click()
        displayDownloadButtons.value = false
      })
  }
  async function refreshGpx(workoutId: string) {
    store.dispatch(WORKOUTS_STORE.ACTIONS.REFRESH_WORKOUT, workoutId)
  }

  function displayDeleteModal() {
    emit('displayModal', true)
  }
  function updateLike(workout: IWorkoutObject) {
    store.dispatch(
      workout.liked
        ? WORKOUTS_STORE.ACTIONS.UNDO_LIKE_WORKOUT
        : WORKOUTS_STORE.ACTIONS.LIKE_WORKOUT,
      workout.workoutId
    )
  }
  function displayReportForm() {
    store.commit(WORKOUTS_STORE.MUTATIONS.SET_CURRENT_REPORTING, true)
  }
  function toggleDownloadButtons() {
    displayDownloadButtons.value = !displayDownloadButtons.value
  }
  function hideDownloadButtons(event: Event) {
    event.stopPropagation()
    if (
      (event.target as Element).id !== null &&
      ['download-workout', 'download-workout-icon'].includes(
        (event.target as Element).id
      )
    ) {
      return
    }
    displayDownloadButtons.value = false
  }

  watch(
    () => workoutObject.value.workoutId,
    () => {
      displayDownloadButtons.value = false
    }
  )
</script>

<style lang="scss" scoped>
  @use '~@/scss/vars.scss' as *;

  #workout-card-title {
    display: flex;
    justify-content: space-between;
    align-items: center;

    .workout-arrow {
      cursor: pointer;
      padding: $default-padding;
      &.inactive {
        color: var(--disabled-color);
        cursor: default;
      }
    }

    .workout-card-title {
      display: flex;
      flex-grow: 1;
      align-items: center;
      .sport-img {
        padding: 0 $default-padding;
        ::v-deep(svg) {
          height: 35px;
          width: 35px;
        }
      }
      .workout-title {
        display: flex;
        flex-direction: row;
        align-items: baseline;
        span {
          margin-right: $default-margin * 0.5;
        }
      }
      .likes-count {
        font-weight: normal;
        padding: 0 $default-margin * 0.5 0 $default-margin * 0.25;
      }
      .workout-date {
        font-size: 0.8em;
        font-weight: normal;
      }
      .workout-segment {
        font-weight: normal;
      }
      .workout-link {
        padding-left: $default-padding;
      }

      .workout-buttons {
        display: flex;
        .download-files {
          .download-files-buttons {
            position: absolute;
            z-index: 1010;

            display: flex;
            flex-direction: column;
            align-items: flex-start;
            margin-top: $default-margin;
            margin-left: -8px;

            background-color: var(--dropdown-background-color);
            box-shadow: 2px 2px 5px var(--app-shadow-color);
            border-radius: $border-radius;

            button {
              margin: 0;
              padding: $default-padding;
              width: 100%;
              border: none;
              text-align: left;

              &:hover,
              &:focus {
                background-color: var(--dropdown-hover-color);
              }
            }
          }
        }
      }

      .refresh-message {
        font-size: 0.85em;
        font-style: italic;
        font-weight: normal;
      }

      .fa {
        padding: 0 $default-padding * 0.3;
      }
      .fa-heart.liked {
        color: var(--like-color);
      }
      .icon-button {
        margin-left: 2px;
      }
    }

    @media screen and (max-width: $small-limit) {
      .workout-arrow {
        padding: $default-padding * 0.5;
      }
      .workout-card-title {
        @media screen and (max-width: $small-limit) {
          .fa-download,
          .fa-trash,
          .fa-edit {
            padding: 0 $default-padding * 0.7;
          }
        }

        .workout-title {
          display: flex;
          flex-direction: column;
        }
      }
    }
  }
</style>
