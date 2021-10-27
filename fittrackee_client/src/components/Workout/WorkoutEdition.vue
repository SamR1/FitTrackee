<template>
  <div
    id="workout-edition"
    class="center-card center-card with-margin"
    :class="{ 'center-form': workout && workout.with_gpx }"
  >
    <Card>
      <template #title>{{
        $t(`workouts.${isCreation ? 'ADD' : 'EDIT'}_WORKOUT`)
      }}</template>
      <template #content>
        <div id="workout-form">
          <form @submit.prevent="updateWorkout">
            <div class="form-items">
              <div class="form-item-radio" v-if="isCreation">
                <div>
                  <input
                    id="withGpx"
                    type="radio"
                    :checked="withGpx"
                    :disabled="loading"
                    @click="updateWithGpx"
                  />
                  <label for="withGpx">{{ $t('workouts.WITH_GPX') }}</label>
                </div>
                <div>
                  <input
                    id="withoutGpx"
                    type="radio"
                    :checked="!withGpx"
                    :disabled="loading"
                    @click="updateWithGpx"
                  />
                  <label for="withoutGpx">{{
                    $t('workouts.WITHOUT_GPX')
                  }}</label>
                </div>
              </div>
              <div class="form-item">
                <label> {{ $t('workouts.SPORT', 1) }}: </label>
                <select
                  id="sport"
                  required
                  :disabled="loading"
                  v-model="workoutDataObject.sport_id"
                >
                  <option
                    v-for="sport in translatedSports.filter((s) => s.is_active)"
                    :value="sport.id"
                    :key="sport.id"
                  >
                    {{ sport.label }}
                  </option>
                </select>
              </div>
              <div class="form-item" v-if="isCreation && withGpx">
                <label for="gpxFile">
                  {{ $t('workouts.GPX_FILE') }}
                  {{ $t('workouts.ZIP_ARCHIVE_DESCRIPTION') }}:
                </label>
                <input
                  id="gpxFile"
                  name="gpxFile"
                  type="file"
                  accept=".gpx, .zip"
                  :disabled="loading"
                  @input="updateFile"
                />
                <div class="files-help info-box">
                  <div>
                    <strong>{{ $t('workouts.GPX_FILE') }}:</strong>
                    <ul>
                      <li>
                        {{ $t('workouts.MAX_SIZE') }}: {{ fileSizeLimit }}
                      </li>
                    </ul>
                  </div>
                  <div>
                    <strong>{{ $t('workouts.ZIP_ARCHIVE') }}:</strong>
                    <ul>
                      <li>{{ $t('workouts.NO_FOLDER') }}</li>
                      <li>
                        {{ $t('workouts.MAX_FILES') }}: {{ gpx_limit_import }}
                      </li>
                      <li>{{ $t('workouts.MAX_SIZE') }}: {{ zipSizeLimit }}</li>
                    </ul>
                  </div>
                </div>
              </div>
              <div class="form-item" v-else>
                <label for="title"> {{ $t('workouts.TITLE') }}: </label>
                <input
                  id="title"
                  name="title"
                  type="text"
                  :required="!isCreation"
                  :disabled="loading"
                  v-model="workoutDataObject.title"
                />
              </div>
              <div v-if="!withGpx">
                <div class="workout-date-duration">
                  <div class="form-item">
                    <label>{{ $t('workouts.WORKOUT_DATE') }}:</label>
                    <div class="workout-date-time">
                      <input
                        id="workout-date"
                        name="workout-date"
                        type="date"
                        required
                        :disabled="loading"
                        v-model="workoutDataObject.workoutDate"
                      />
                      <input
                        id="workout-time"
                        name="workout-time"
                        class="workout-time"
                        type="time"
                        required
                        :disabled="loading"
                        v-model="workoutDataObject.workoutTime"
                      />
                    </div>
                  </div>
                  <div class="form-item">
                    <label>{{ $t('workouts.DURATION') }}:</label>
                    <div>
                      <input
                        id="workout-duration-hour"
                        name="workout-duration-hour"
                        class="workout-duration"
                        type="text"
                        placeholder="HH"
                        pattern="^([0-9]*[0-9])$"
                        required
                        :disabled="loading"
                        v-model="workoutDataObject.workoutDurationHour"
                      />
                      :
                      <input
                        id="workout-duration-minutes"
                        name="workout-duration-minutes"
                        class="workout-duration"
                        type="text"
                        pattern="^([0-5][0-9])$"
                        placeholder="MM"
                        required
                        :disabled="loading"
                        v-model="workoutDataObject.workoutDurationMinutes"
                      />
                      :
                      <input
                        id="workout-duration-seconds"
                        name="workout-duration-seconds"
                        class="workout-duration"
                        type="text"
                        pattern="^([0-5][0-9])$"
                        placeholder="SS"
                        required
                        :disabled="loading"
                        v-model="workoutDataObject.workoutDurationSeconds"
                      />
                    </div>
                  </div>
                </div>
                <div class="form-item">
                  <label>{{ $t('workouts.DISTANCE') }} (km):</label>
                  <input
                    type="number"
                    min="0"
                    step="0.1"
                    required
                    :disabled="loading"
                    v-model="workoutDataObject.workoutDistance"
                  />
                </div>
              </div>
              <div class="form-item">
                <label> {{ $t('workouts.NOTES') }}: </label>
                <CustomTextArea
                  name="notes"
                  :input="workoutDataObject.notes"
                  :disabled="loading"
                  @updateValue="updateNotes"
                />
              </div>
            </div>
            <ErrorMessage :message="errorMessages" v-if="errorMessages" />
            <div v-if="loading">
              <Loader />
            </div>
            <div v-else class="form-buttons">
              <button class="confirm" type="submit" :disabled="loading">
                {{ $t('buttons.SUBMIT') }}
              </button>
              <button class="cancel" @click.prevent="onCancel">
                {{ $t('buttons.CANCEL') }}
              </button>
            </div>
          </form>
        </div>
      </template>
    </Card>
  </div>
</template>

<script lang="ts">
  import {
    ComputedRef,
    PropType,
    defineComponent,
    computed,
    reactive,
    ref,
    watch,
    onMounted,
    onUnmounted,
  } from 'vue'
  import { useI18n } from 'vue-i18n'
  import { useRouter } from 'vue-router'

  import { ROOT_STORE, WORKOUTS_STORE } from '@/store/constants'
  import { TAppConfig } from '@/types/application'
  import { ISport } from '@/types/sports'
  import { IAuthUserProfile } from '@/types/user'
  import { IWorkout, IWorkoutForm } from '@/types/workouts'
  import { useStore } from '@/use/useStore'
  import { formatWorkoutDate, getDateWithTZ } from '@/utils/dates'
  import { getReadableFileSize } from '@/utils/files'
  import { translateSports } from '@/utils/sports'

  export default defineComponent({
    name: 'WorkoutEdition',
    props: {
      authUser: {
        type: Object as PropType<IAuthUserProfile>,
        required: true,
      },
      isCreation: {
        type: Boolean,
        default: false,
      },
      loading: {
        type: Boolean,
        default: false,
      },
      sports: {
        type: Object as PropType<ISport[]>,
        required: true,
      },
      workout: {
        type: Object as PropType<IWorkout>,
        required: false,
      },
    },
    setup(props) {
      const { t } = useI18n()
      const store = useStore()
      const router = useRouter()

      onMounted(() => {
        if (props.workout && props.workout.id) {
          formatWorkoutForm(props.workout)
        }
      })

      const translatedSports: ComputedRef<ISport[]> = computed(() =>
        translateSports(props.sports, t)
      )
      const appConfig: ComputedRef<TAppConfig> = computed(
        () => store.getters[ROOT_STORE.GETTERS.APP_CONFIG]
      )
      const fileSizeLimit = appConfig.value.max_single_file_size
        ? getReadableFileSize(appConfig.value.max_single_file_size)
        : ''
      const gpx_limit_import = appConfig.value.gpx_limit_import
      const zipSizeLimit = appConfig.value.max_zip_file_size
        ? getReadableFileSize(appConfig.value.max_zip_file_size)
        : ''
      const errorMessages: ComputedRef<string | string[] | null> = computed(
        () => store.getters[ROOT_STORE.GETTERS.ERROR_MESSAGES]
      )
      const workoutForm = reactive({
        sport_id: '',
        title: '',
        notes: '',
        workoutDate: '',
        workoutTime: '',
        workoutDurationHour: '',
        workoutDurationMinutes: '',
        workoutDurationSeconds: '',
        workoutDistance: '',
      })
      let withGpx = ref(
        props.workout ? props.workout.with_gpx : props.isCreation
      )
      let gpxFile: File | null = null

      function updateNotes(value: string) {
        workoutForm.notes = value
      }
      function updateWithGpx() {
        withGpx.value = !withGpx.value
      }
      function updateFile(event: Event & { target: HTMLInputElement }) {
        if (event.target.files) {
          gpxFile = event.target.files[0]
        }
      }
      function formatWorkoutForm(workout: IWorkout) {
        workoutForm.sport_id = `${workout.sport_id}`
        workoutForm.title = workout.title
        workoutForm.notes = workout.notes
        if (!workout.with_gpx) {
          const workoutDateTime = formatWorkoutDate(
            getDateWithTZ(workout.workout_date, props.authUser.timezone),
            'yyyy-MM-dd'
          )
          const duration = workout.duration.split(':')
          workoutForm.workoutDistance = `${workout.distance}`
          workoutForm.workoutDate = workoutDateTime.workout_date
          workoutForm.workoutTime = workoutDateTime.workout_time
          workoutForm.workoutDurationHour = duration[0]
          workoutForm.workoutDurationMinutes = duration[1]
          workoutForm.workoutDurationSeconds = duration[2]
        }
      }
      function formatPayload(payload: IWorkoutForm) {
        payload.title = workoutForm.title
        payload.distance = +workoutForm.workoutDistance
        payload.duration =
          +workoutForm.workoutDurationHour * 3600 +
          +workoutForm.workoutDurationMinutes * 60 +
          +workoutForm.workoutDurationSeconds
        payload.workout_date = `${workoutForm.workoutDate} ${workoutForm.workoutTime}`
      }
      function updateWorkout() {
        const payload: IWorkoutForm = {
          sport_id: +workoutForm.sport_id,
          notes: workoutForm.notes,
        }
        if (props.workout) {
          if (props.workout.with_gpx) {
            store.dispatch(WORKOUTS_STORE.ACTIONS.EDIT_WORKOUT, {
              workoutId: props.workout.id,
              data: payload,
            })
          } else {
            formatPayload(payload)
            store.dispatch(
              WORKOUTS_STORE.ACTIONS.ADD_WORKOUT_WITHOUT_GPX,
              payload
            )
          }
        } else {
          if (withGpx.value) {
            if (!gpxFile) {
              throw new Error('No file provided !!')
            }
            payload.file = gpxFile
            store.dispatch(WORKOUTS_STORE.ACTIONS.ADD_WORKOUT, payload)
          } else {
            formatPayload(payload)
            store.dispatch(
              WORKOUTS_STORE.ACTIONS.ADD_WORKOUT_WITHOUT_GPX,
              payload
            )
          }
        }
      }
      function onCancel() {
        if (props.workout) {
          router.push({
            name: 'Workout',
            params: { workoutId: props.workout.id },
          })
        } else {
          router.go(-1)
        }
      }

      watch(
        () => props.workout,
        async (
          newWorkout: IWorkout | undefined,
          previousWorkout: IWorkout | undefined
        ) => {
          if (newWorkout !== previousWorkout && newWorkout && newWorkout.id) {
            formatWorkoutForm(newWorkout)
          }
        }
      )

      onUnmounted(() => store.commit(ROOT_STORE.MUTATIONS.EMPTY_ERROR_MESSAGES))

      return {
        appConfig,
        errorMessages,
        fileSizeLimit,
        gpx_limit_import,
        translatedSports,
        withGpx,
        zipSizeLimit,
        workoutDataObject: workoutForm,
        onCancel,
        updateFile,
        updateNotes,
        updateWithGpx,
        updateWorkout,
      }
    },
  })
</script>

<style lang="scss" scoped>
  @import '~@/scss/base';

  #workout-edition {
    @media screen and (max-width: $small-limit) {
      &.center-form {
        margin: 50px auto;
      }
    }

    ::v-deep(.card) {
      .card-title {
        text-align: center;
        text-transform: uppercase;
      }

      .card-content {
        @media screen and (max-width: $medium-limit) {
          padding: $default-padding 0;
        }

        #workout-form {
          .form-items {
            display: flex;
            flex-direction: column;

            input {
              height: 20px;
            }

            .workout-date-duration {
              display: flex;
              flex-direction: row;
              justify-content: space-between;

              @media screen and (max-width: $medium-limit) {
                flex-direction: column;
              }
            }

            .form-item {
              display: flex;
              flex-direction: column;
              padding: $default-padding;

              .workout-date-time {
                display: flex;
                #workout-date {
                  margin-right: $default-margin;
                }
              }

              .workout-duration {
                width: 25px;
              }
            }

            .form-item-radio {
              display: flex;
              justify-content: space-around;
              label {
                font-weight: normal;
                @media screen and (max-width: $medium-limit) {
                  font-size: 0.9em;
                }
              }
              input {
                margin-top: -2px;
                vertical-align: middle;
              }
            }
          }

          .form-buttons {
            display: flex;
            justify-content: flex-end;
            button {
              margin: $default-padding * 0.5;
            }
          }

          .files-help {
            display: flex;
            justify-content: space-around;
            margin-top: $default-margin;
            div {
              display: flex;
              @media screen and (max-width: $medium-limit) {
                flex-direction: column;
              }
              ul {
                margin: 0;
                padding: 0 $default-padding * 2;
              }
            }
          }
        }
      }
    }
  }
</style>
