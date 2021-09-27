<template>
  <div class="timeline-workout">
    <Card>
      <template #content>
        <div class="workout-user-date">
          <div class="workout-user">
            <img
              class="profile-img"
              v-if="userPictureUrl !== ''"
              alt="User picture"
              :src="userPictureUrl"
            />
            <div v-else class="no-picture">
              <i class="fa fa-user-circle-o" aria-hidden="true" />
            </div>
            <span v-if="user.username" class="workout-user-name">
              {{ user.username }}
            </span>
          </div>
          <div
            class="workout-date"
            v-if="workout && user"
            :title="
              format(
                getDateWithTZ(workout.workout_date, user.timezone),
                'dd/MM/yyyy HH:mm'
              )
            "
          >
            {{
              formatDistance(new Date(workout.workout_date), new Date(), {
                addSuffix: true,
                locale,
              })
            }}
          </div>
        </div>
        <div
          class="workout-map"
          :class="{ 'no-cursor': !workout }"
          @click="
            workout
              ? $router.push({
                  name: 'Workout',
                  params: { workoutId: workout.id },
                })
              : null
          "
        >
          <div v-if="workout">
            <StaticMap v-if="workout.with_gpx" :workout="workout" />
            <div v-else class="no-map">
              {{ t('workouts.NO_MAP') }}
            </div>
          </div>
        </div>
        <div
          class="workout-data"
          @click="
            $router.push({ name: 'Workout', params: { workoutId: workout.id } })
          "
        >
          <div>
            <img
              v-if="sport"
              class="sport-img"
              alt="workout sport logo"
              :src="sport.img"
            />
          </div>
          <div>
            <i class="fa fa-clock-o" aria-hidden="true" />
            <span v-if="workout">{{ workout.moving }}</span>
          </div>
          <div>
            <i class="fa fa-road" aria-hidden="true" />
            <span v-if="workout">{{ workout.distance }} km</span>
          </div>
        </div>
      </template>
    </Card>
  </div>
</template>

<script lang="ts">
  import { Locale, format, formatDistance } from 'date-fns'
  import { PropType, defineComponent, ComputedRef, computed } from 'vue'
  import { useI18n } from 'vue-i18n'

  import Card from '@/components/Common/Card.vue'
  import StaticMap from '@/components/Common/StaticMap.vue'
  import { ROOT_STORE } from '@/store/constants'
  import { ISport } from '@/types/sports'
  import { IAuthUserProfile } from '@/types/user'
  import { IWorkout } from '@/types/workouts'
  import { useStore } from '@/use/useStore'
  import { getApiUrl } from '@/utils'
  import { getDateWithTZ } from '@/utils/dates'

  export default defineComponent({
    name: 'WorkoutCard',
    components: {
      Card,
      StaticMap,
    },
    props: {
      workout: {
        type: Object as PropType<IWorkout>,
        required: false,
      },
      user: {
        type: Object as PropType<IAuthUserProfile>,
        required: true,
      },
      sport: {
        type: Object as PropType<ISport>,
        required: false,
      },
    },
    setup(props) {
      const { t } = useI18n()
      const store = useStore()

      const userPictureUrl: ComputedRef<string> = computed(() =>
        props.user.picture
          ? `${getApiUrl()}/users/${props.user.username}/picture?${Date.now()}`
          : ''
      )
      const locale: ComputedRef<Locale> = computed(
        () => store.getters[ROOT_STORE.GETTERS.LOCALE]
      )

      return {
        format,
        formatDistance,
        getDateWithTZ,
        locale,
        t,
        userPictureUrl,
      }
    },
  })
</script>

<style lang="scss" scoped>
  @import '~@/scss/base';

  .timeline-workout {
    margin-bottom: $default-margin * 2;

    ::v-deep(.card) {
      .card-content {
        display: flex;
        flex-direction: column;
        padding: 0;
        .workout-user-date {
          display: flex;
          justify-content: space-between;
          padding: $default-padding * 0.5 $default-padding;
          .workout-user {
            display: flex;
            .profile-img {
              border-radius: 50%;
              height: 25px;
              width: 25px;
            }
            .fa-user-circle-o {
              font-size: 1.5em;
            }
            .workout-user-name {
              padding-left: 5px;
            }
          }
          .workout-date {
            font-size: 0.85em;
            font-style: italic;
          }
        }

        .workout-map {
          background-color: var(--workout-no-map-bg-color);
          height: 150px;
          .no-map {
            line-height: 150px;
          }
          .bg-map-image {
            height: 150px;
          }
        }

        .workout-data {
          display: flex;
          padding-top: $default-padding * 0.5;
          .sport-img {
            height: 28px;
            width: 28px;
          }
          div {
            width: 33%;
            text-align: center;
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
  }
</style>
