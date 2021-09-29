<template>
  <div id="workout-edition">
    <Card :without-title="false">
      <template #title>{{
        t(`workouts.${isCreation ? 'ADD' : 'EDIT'}_WORKOUT`)
      }}</template>
      <template #content>
        <div id="workout-form">
          <form @submit.prevent="updateWorkout">
            <div class="form-items">
              <div class="form-item-radio" v-if="isCreation">
                <div class="radio">
                  <input
                    id="withGpx"
                    type="radio"
                    :checked="withGpx"
                    :disabled="loading"
                    @click="updateWithGpx"
                  />
                  <label for="withGpx">{{ t('workouts.WITH_GPX') }}</label>
                </div>
                <div class="radio">
                  <input
                    id="withoutGpx"
                    type="radio"
                    :checked="!withGpx"
                    :disabled="loading"
                    @click="updateWithGpx"
                  />
                  <label for="withoutGpx">{{
                    t('workouts.WITHOUT_GPX')
                  }}</label>
                </div>
              </div>
              <div class="form-item">
                <label> {{ t('workouts.SPORT', 1) }}: </label>
                <select
                  id="sport"
                  required
                  :disabled="loading"
                  v-model="workoutDataObject.sport_id"
                >
                  <option
                    v-for="sport in translatedSports"
                    :value="sport.id"
                    :key="sport.id"
                  >
                    {{ sport.label }}
                  </option>
                </select>
              </div>
              <div class="form-item" v-if="isCreation && withGpx">
                <label for="gpxFile">
                  {{ t('workouts.GPX_FILE') }}
                  <sup>
                    <i class="fa fa-question-circle" aria-hidden="true" />
                  </sup>
                  {{ t('workouts.ZIP_FILE') }}
                  <sup
                    ><i class="fa fa-question-circle" aria-hidden="true" /></sup
                  >:
                </label>
                <input
                  id="gpxFile"
                  name="gpxFile"
                  type="file"
                  accept=".gpx, .zip"
                  :disabled="loading"
                  @input="updateFile"
                />
              </div>
              <div class="form-item" v-else>
                <label for="title"> {{ t('workouts.TITLE') }}: </label>
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
                    <label>{{ t('workouts.WORKOUT_DATE') }}:</label>
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
                    <label>{{ t('workouts.DURATION') }}:</label>
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
                  <label>{{ t('workouts.DISTANCE') }} (km):</label>
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
                <label> {{ t('workouts.NOTES') }}: </label>
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
                {{ t('buttons.SUBMIT') }}
              </button>
              <button class="cancel" @click.prevent="onCancel">
                {{ t('buttons.CANCEL') }}
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

  import Card from '@/components/Common/Card.vue'
  import CustomTextArea from '@/components/Common/CustomTextArea.vue'
  import ErrorMessage from '@/components/Common/ErrorMessage.vue'
  import Loader from '@/components/Common/Loader.vue'
  import { ROOT_STORE, WORKOUTS_STORE } from '@/store/constants'
  import { ISport } from '@/types/sports'
  import { IAuthUserProfile } from '@/types/user'
  import { IWorkout, IWorkoutForm } from '@/types/workouts'
  import { useStore } from '@/use/useStore'
  import { formatWorkoutDate, getDateWithTZ } from '@/utils/dates'
  import { translateSports } from '@/utils/sports'

  export default defineComponent({
    name: 'WorkoutEdition',
    components: {
      Card,
      CustomTextArea,
      ErrorMessage,
      Loader,
    },
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
        errorMessages,
        t,
        translatedSports,
        withGpx,
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
    margin: 100px auto;
    width: 700px;
    @media screen and (max-width: $small-limit) {
      width: 100%;
      margin: 0 auto 50px auto;
    }

    ::v-deep(.card) {
      .card-title {
        text-align: center;
        text-transform: uppercase;
      }

      .card-content {
        @media screen and (max-width: $small-limit) {
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

              @media screen and (max-width: $small-limit) {
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
              .radio {
                label {
                  font-weight: normal;
                }
                input {
                  margin-top: -2px;
                  vertical-align: middle;
                }
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
        }
      }
    }
  }
</style>
