<template>
  <div id="workout-card-title">
    <button
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
      <div class="workout-title-date">
        <div class="workout-title" v-if="workoutObject.type === 'WORKOUT'">
          <span>{{ workoutObject.title }}</span>
          <a
            class="remote-link"
            v-if="workoutObject.remoteUrl"
            :href="workoutObject.remoteUrl"
            target="_blank"
            rel="noopener noreferrer"
          >
            {{ $t('workouts.VIEW_ON_REMOTE_INSTANCE') }}
            <i class="fa fa-external-link-square" aria-hidden="true"></i>
          </a>
          <button
            class="transparent icon-button likes"
            @click="updateLike(workoutObject)"
          >
            <i
              class="fa"
              :class="`fa-heart${workoutObject.liked ? '' : '-o'}`"
            />
            <span class="likes-count" v-if="workoutObject.likes_count > 0">{{
              workoutObject.likes_count
            }}</span>
          </button>
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
            @click="displayDeleteModal"
            :aria-label="$t(`workouts.DELETE_WORKOUT`)"
          >
            <i class="fa fa-trash" aria-hidden="true" />
          </button>
        </div>
        <div class="workout-title" v-else>
          {{ workoutObject.title }}
          <span class="workout-segment">
            —
            <i class="fa fa-map-marker" aria-hidden="true" />
            {{ $t('workouts.SEGMENT') }}
            {{ workoutObject.segmentId + 1 }}
          </span>
        </div>
        <div class="workout-date">
          <time>
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
  import { toRefs } from 'vue'

  import authApi from '@/api/authApi'
  import { WORKOUTS_STORE } from '@/store/constants'
  import { ISport } from '@/types/sports'
  import { IWorkoutObject } from '@/types/workouts'
  import { useStore } from '@/use/useStore'

  interface Props {
    sport: ISport
    workoutObject: IWorkoutObject
    isWorkoutOwner: boolean
  }
  const props = defineProps<Props>()

  const store = useStore()

  const emit = defineEmits(['displayModal'])

  const { isWorkoutOwner, sport, workoutObject } = toRefs(props)

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
  function displayDeleteModal(event: Event & { target: HTMLInputElement }) {
    event.target.blur()
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
</script>

<style lang="scss" scoped>
  @import '~@/scss/vars.scss';

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
        .remote-link {
          font-size: 0.85em;
          font-style: italic;
          font-weight: normal;

          .fa-external-link-square {
            font-size: 0.85em;
            padding: 0;
          }
        }
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
      .icon-button {
        cursor: pointer;
        padding: 0;
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
