<template>
  <div class="timeline-workout workout-card">
    <div class="box">
      <div class="workout-card-title">
        <div class="workout-user-date">
          <div class="workout-user">
            <UserPicture :user="user" />
            <Username :user="user" />
          </div>
          <router-link
            class="workout-title"
            v-if="workout.id"
            :to="{
              name: 'Workout',
              params: { workoutId: workout.id },
            }"
          >
            {{ workout.title }}
          </router-link>
          <div class="workout-date-visibility">
            <time
              class="workout-date"
              v-if="workout.workout_date && user"
              :datetime="workoutDateWithTZ"
              :title="workoutDateWithTZ"
            >
              {{
                formatDistance(new Date(workout.workout_date), new Date(), {
                  addSuffix: true,
                  locale,
                })
              }}
            </time>
            <VisibilityIcon :visibility="workout.workout_visibility" />
          </div>
        </div>
        <div v-if="user.is_remote" class="user-remote-fullname">
          {{ user.fullname }}
        </div>
      </div>
      <div class="workout-map">
        <StaticMap v-if="workout.with_gpx" :workout="workout" />
        <router-link
          v-else-if="workout.id"
          :to="{
            name: 'Workout',
            params: { workoutId: workout.id },
          }"
        >
          <div class="no-map">
            {{ $t('workouts.NO_MAP') }}
          </div>
        </router-link>
      </div>
      <div
        class="workout-data"
        :class="{ 'without-elevation': !hasElevation(workout) }"
        @click="
          workout.id
            ? $router.push({
                name: 'Workout',
                params: { workoutId: workout.id },
              })
            : null
        "
      >
        <div class="img">
          <SportImage
            v-if="sport?.label"
            :sport-label="sport.label"
            :color="sport.color"
          />
        </div>
        <div class="data">
          <i class="fa fa-clock-o" aria-hidden="true" />
          <span v-if="workout">{{ workout.moving }}</span>
        </div>
        <div class="data">
          <i class="fa fa-road" aria-hidden="true" />
          <Distance
            v-if="workout.id"
            :distance="workout.distance"
            :digits="3"
            unitFrom="km"
            :useImperialUnits="useImperialUnits"
          />
        </div>
        <div class="data elevation" v-if="hasElevation(workout)">
          <img
            class="mountains"
            src="/img/workouts/mountains.svg"
            :alt="$t('workouts.ELEVATION')"
          />
          <div class="data-values">
            <Distance
              v-if="workout.id"
              :distance="workout.min_alt"
              unitFrom="m"
              :displayUnit="false"
              :useImperialUnits="useImperialUnits"
            />/
            <Distance
              v-if="workout.id"
              :distance="workout.max_alt"
              unitFrom="m"
              :useImperialUnits="useImperialUnits"
            />
          </div>
        </div>
        <div class="data altitude" v-if="hasUphillValue(workout)">
          <i class="fa fa-location-arrow" aria-hidden="true" />
          <div class="data-values">
            +<Distance
              v-if="workout.id"
              :distance="workout.ascent"
              unitFrom="m"
              :displayUnit="false"
              :useImperialUnits="useImperialUnits"
            />/-
            <Distance
              v-if="workout.id"
              :distance="workout.descent"
              unitFrom="m"
              :useImperialUnits="useImperialUnits"
            />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
  import { formatDistance } from 'date-fns'
  import type { Locale } from 'date-fns'
  import { computed, toRefs } from 'vue'
  import type { ComputedRef } from 'vue'

  import StaticMap from '@/components/Common/StaticMap.vue'
  import Username from '@/components/User/Username.vue'
  import UserPicture from '@/components/User/UserPicture.vue'
  import { ROOT_STORE } from '@/store/constants'
  import type { ISport } from '@/types/sports'
  import type { IUserProfile } from '@/types/user'
  import type { IWorkout } from '@/types/workouts'
  import { useStore } from '@/use/useStore'
  import { formatDate } from '@/utils/dates'

  interface Props {
    user: IUserProfile
    useImperialUnits: boolean
    dateFormat: string
    timezone: string
    workout?: IWorkout
    sport?: ISport | null
  }
  const props = withDefaults(defineProps<Props>(), {
    workout: () => ({}) as IWorkout,
    sport: () => ({}) as ISport,
  })

  const store = useStore()

  const { dateFormat, sport, timezone, user, useImperialUnits, workout } =
    toRefs(props)
  const locale: ComputedRef<Locale> = computed(
    () => store.getters[ROOT_STORE.GETTERS.LOCALE]
  )
  const workoutDateWithTZ = computed(() =>
    formatDate(workout.value.workout_date, timezone.value, dateFormat.value)
  )

  function hasElevation(workout: IWorkout): boolean {
    return (
      workout.with_gpx && workout.min_alt !== null && workout.max_alt !== null
    )
  }
  function hasUphillValue(workout: IWorkout): boolean {
    return (
      hasElevation(workout) &&
      workout.ascent !== null &&
      workout.descent !== null
    )
  }
</script>

<style lang="scss" scoped>
  @import '~@/scss/vars.scss';

  .mountains {
    padding-right: $default-padding * 0.5;
  }

  .timeline-workout {
    margin-bottom: $default-margin * 2;

    .box {
      flex-direction: column;
      padding: 0;
      .workout-user-date {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        padding: $default-padding * 0.5 $default-padding;
        .workout-user {
          display: flex;
          ::v-deep(.user-picture) {
            min-width: min-content;
            img {
              height: 25px;
              width: 25px;
            }
            .no-picture {
              font-size: 1.5em;
            }
          }
          .workout-user-name {
            white-space: nowrap;
            margin-left: 3px;
            padding: 0 5px;
            text-decoration: none;
          }
        }
        .workout-date-visibility {
          display: flex;
          gap: 5px;
          align-items: flex-end;

          .workout-date {
            font-size: 0.85em;
            font-style: italic;
            white-space: nowrap;
          }
        }
        .workout-title {
          display: block;
          text-align: center;
          padding: 0 $default-padding;
          @media screen and (max-width: $x-small-limit) {
            display: none;
          }
        }
      }

      .user-remote-fullname {
        font-size: 0.8em;
        font-style: italic;
        margin-top: -0.5 * $default-padding;
        padding-left: $default-padding;
      }

      .workout-map {
        height: 150px;
        .no-map {
          line-height: 150px;
          filter: var(--no-map-filter);
        }
        ::v-deep(.static-map) {
          background-color: var(--workout-static-map-bg-color);
          .bg-map-image {
            height: 150px;
          }
        }
      }

      .workout-data {
        display: flex;
        padding: $default-padding * 0.5;
        font-size: 0.9em;
        .sport-img {
          height: 25px;
          width: 25px;
        }
        .img,
        .data {
          display: flex;
          align-items: center;
          .data-values {
            display: flex;
            flex-wrap: wrap;
          }
        }
        .img {
          justify-content: flex-end;
          width: 10%;
        }
        .data {
          justify-content: center;
          width: 22%;
        }
        @media screen and (max-width: $x-small-limit) {
          .img {
            justify-content: center;
            width: 20%;
          }
          .data {
            justify-content: center;
            width: 40%;
          }
          .altitude,
          .elevation {
            display: none;
          }
        }

        &.without-elevation {
          .img,
          .data {
            justify-content: center;
            width: 33%;
          }
        }
      }

      .workout-map,
      .workout-data {
        cursor: pointer;
      }
      .no-cursor {
        cursor: default;
      }
      .fa {
        padding-right: $default-padding;
      }
    }
  }
</style>
