<template>
  <div id="workout-card-title">
    <button
      v-if="isWorkoutOwner"
      class="workout-previous workout-arrow transparent"
      :class="{ inactive: !workoutObject.previousUrl }"
      :disabled="!workoutObject.previousUrl"
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
          <div v-if="isAuthenticated">
            <button
              class="transparent icon-button likes"
              @click="updateLike(workoutObject)"
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
              v-if="isWorkoutOwner"
              @click="
                $router.push({
                  name: 'EditWorkout',
                  params: { workoutId: workoutObject.workoutId },
                })
              "
              :aria-label="$t(`workouts.EDIT_WORKOUT`)"
            >
              <i class="fa fa-edit" aria-hidden="true" />
            </button>
            <button
              v-if="workoutObject.with_gpx && isWorkoutOwner"
              class="transparent icon-button"
              @click.prevent="downloadGpx(workoutObject.workoutId)"
              :aria-label="$t(`workouts.DOWNLOAD_WORKOUT`)"
            >
              <i class="fa fa-download" aria-hidden="true" />
            </button>
            <button
              v-if="isWorkoutOwner"
              id="delete-workout-button"
              class="transparent icon-button"
              @click.prevent="displayDeleteModal"
              :aria-label="$t(`workouts.DELETE_WORKOUT`)"
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
      v-if="isWorkoutOwner"
      class="workout-next workout-arrow transparent"
      :class="{ inactive: !workoutObject.nextUrl }"
      :disabled="!workoutObject.nextUrl"
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
  import { computed, toRefs } from 'vue'
  import type { ComputedRef } from 'vue'

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
  }
  const props = defineProps<Props>()
  const { isWorkoutOwner, sport, workoutObject } = toRefs(props)

  const emit = defineEmits(['displayModal'])

  const store = useStore()

  const { isAuthenticated } = useAuthUser()

  const currentlyReporting: ComputedRef<boolean> = computed(
    () => store.getters[WORKOUTS_STORE.GETTERS.CURRENT_REPORTING]
  )
  const reportStatus: ComputedRef<string | null> = computed(
    () => store.getters[REPORTS_STORE.GETTERS.REPORT_STATUS]
  )

  async function downloadGpx(workoutId: string) {
    await authApi
      .get(`workouts/${workoutId}/gpx/download`, {
        responseType: 'blob',
      })
      .then((response) => {
        const gpxFileUrl = window.URL.createObjectURL(
          new Blob([response.data], { type: 'application/gpx+xml' })
        )
        const gpxLink = document.createElement('a')
        gpxLink.href = gpxFileUrl
        gpxLink.setAttribute('download', `${workoutId}.gpx`)
        document.body.appendChild(gpxLink)
        gpxLink.click()
      })
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
