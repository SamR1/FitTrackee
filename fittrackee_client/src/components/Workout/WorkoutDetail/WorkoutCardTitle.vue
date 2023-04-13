<template>
  <div id="workout-card-title">
    <div
      v-if="isWorkoutOwner"
      class="workout-previous workout-arrow"
      :class="{ inactive: !workoutObject.previousUrl }"
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
    </div>
    <div class="workout-card-title">
      <SportImage :sport-label="sport.label" :color="sport.color" />
      <div class="workout-title-date">
        <div class="workout-title" v-if="workoutObject.type === 'WORKOUT'">
          <span>{{ workoutObject.title }}</span>
          <div class="icons">
            <span class="likes" @click="updateLike(workoutObject)">
              <i class="fa" :class="`fa-heart${workoutObject.liked ? '' : '-o'}`"/>
              <span class="likes-count" v-if="workoutObject.likes_count > 0">{{ workoutObject.likes_count }}</span>
            </span>
            <i
              class="fa fa-edit"
              aria-hidden="true"
              v-if="isWorkoutOwner"
              @click="
                $router.push({
                  name: 'EditWorkout',
                  params: { workoutId: workoutObject.workoutId },
                })
              "
            />
            <i
              v-if="workoutObject.with_gpx && isWorkoutOwner"
              class="fa fa-download"
              aria-hidden="true"
              @click.prevent="downloadGpx(workoutObject.workoutId)"
            />
            <i
              class="fa fa-trash"
              v-if="isWorkoutOwner"
              aria-hidden="true"
              @click="emit('displayModal', true)"
            />
          </div>
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
          {{ workoutObject.workoutDate }} -
          {{ workoutObject.workoutTime }}
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
    <div
      v-if="isWorkoutOwner"
      class="workout-next workout-arrow"
      :class="{ inactive: !workoutObject.nextUrl }"
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
    </div>
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

      .icons {
        .fa {
          cursor: pointer;
          padding: 0 $default-padding * 0.3;
        }

        .fa-heart {
          color: #ee2222;
        }

        .likes {
          padding-left: $default-padding * 0.3;
          margin-right: 0;
          .fa-heart , .fa-heart-o {
            font-size: .95em;
          }
          .likes-count {
            font-size: .9em;
            font-weight: bold;
          }
        }
      }
      @media screen and (max-width: $small-limit) {
        .icons {
          .fa-download,
          .fa-trash,
          .fa-heart,
          .fa-heart-o,
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
