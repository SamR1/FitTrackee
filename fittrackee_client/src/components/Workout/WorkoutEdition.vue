<template>
  <div
    id="workout-edition"
    class="center-card"
    :class="{
      'center-form': workout && workout.with_gpx,
      'with-margin': !isCreation,
    }"
  >
    <Card>
      <template #title>{{
        $t(`workouts.${isCreation ? 'ADD' : 'EDIT'}_WORKOUT`)
      }}</template>
      <template #content>
        <div id="workout-form">
          <form :class="{ errors: formErrors }" @submit.prevent="updateWorkout">
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
                  <label for="withGpx">{{ $t('workouts.WITH_FILE') }}</label>
                </div>
                <div>
                  <input
                    id="withoutGpx"
                    type="radio"
                    :checked="!withGpx"
                    :disabled="loading"
                    @click="updateWithGpx"
                  />
                  <label for="withoutGpx">
                    {{ $t('workouts.WITHOUT_FILE') }}
                  </label>
                </div>
              </div>
              <div class="form-item">
                <label for="sport"> {{ $t('workouts.SPORT', 1) }}*: </label>
                <select
                  id="sport"
                  required
                  @invalid="invalidateForm"
                  :disabled="loading"
                  v-model="workoutForm.sport_id"
                >
                  <option
                    v-for="sport in translatedSports"
                    :value="sport.id"
                    :key="sport.id"
                  >
                    {{ sport.translatedLabel }}
                  </option>
                </select>
              </div>
              <div class="form-item" v-if="isCreation && withGpx">
                <label for="gpxFile">
                  {{ $t('workouts.WORKOUT_FILE') }}
                  {{ $t('workouts.ZIP_ARCHIVE_DESCRIPTION') }}*:
                </label>
                <input
                  id="gpxFile"
                  name="gpxFile"
                  type="file"
                  accept=".gpx, .fit, .kml, .kmz, .tcx, .zip"
                  :disabled="loading"
                  required
                  @invalid="invalidateForm"
                  @input="updateFile"
                />
                <div class="files-info-box info-box">
                  <div class="files-help">
                    <div>
                      <strong>{{ $t('workouts.WORKOUT_FILE') }}:</strong>
                      <ul>
                        <li>
                          {{ $t('workouts.MAX_SIZE') }}: {{ fileSizeLimit }}
                        </li>
                        <li>
                          {{ $t('workouts.SUPPORTED_FILE_EXTENSIONS') }}: .gpx,
                          .fit, .kml, .kmz, .tcx
                        </li>
                      </ul>
                    </div>
                    <div>
                      <strong>{{ $t('workouts.ZIP_ARCHIVE') }}:</strong>
                      <ul>
                        <li>
                          {{ $t('workouts.MAX_SIZE') }}: {{ zipSizeLimit }}
                        </li>
                        <li>
                          {{ $t('workouts.MAX_FILES') }}:
                          {{ fileLimitImport }}
                        </li>
                        <li v-if="asyncUploadEnabled">
                          {{ $t('workouts.MAX_SYNC_FILES_IN_ZIP') }}:
                          {{ fileSyncLimitImport }}
                        </li>
                      </ul>
                    </div>
                  </div>
                  <div
                    class="weather-info"
                    v-if="
                      asyncUploadEnabled && appConfig.weather_provider !== null
                    "
                  >
                    <i class="fa fa-info-circle" aria-hidden="true" />
                    {{ $t('workouts.NO_WEATHER_WITH_ASYNCHRONOUS_UPLOAD') }}
                  </div>
                </div>
              </div>
              <div class="form-item">
                <label for="title">
                  {{ $t('workouts.TITLE') }}{{ isCreation ? '' : '*' }}:
                </label>
                <input
                  id="title"
                  name="title"
                  type="text"
                  :required="!isCreation"
                  @invalid="invalidateForm"
                  :disabled="loading"
                  v-model="workoutForm.title"
                  maxlength="255"
                />
                <div class="field-help" v-if="withGpx && isCreation">
                  <span class="info-box">
                    <i class="fa fa-info-circle" aria-hidden="true" />
                    {{ $t('workouts.TITLE_FIELD_HELP') }}
                  </span>
                </div>
              </div>
              <div v-if="!withGpx">
                <div class="workout-date-duration">
                  <div class="form-item">
                    <label>{{ $t('workouts.WORKOUT_DATE') }}*:</label>
                    <div class="workout-date-time">
                      <input
                        id="workout-date"
                        name="workout-date"
                        type="date"
                        required
                        @invalid="invalidateForm"
                        :disabled="loading"
                        v-model="workoutForm.workoutDate"
                      />
                      <input
                        id="workout-time"
                        name="workout-time"
                        class="workout-time"
                        type="time"
                        required
                        @invalid="invalidateForm"
                        :disabled="loading"
                        v-model="workoutForm.workoutTime"
                      />
                    </div>
                  </div>
                  <div class="form-item">
                    <label>{{ $t('workouts.DURATION') }}*:</label>
                    <div>
                      <label
                        for="workout-duration-hour"
                        class="visually-hidden"
                      >
                        {{ $t('common.HOURS', 0) }}
                      </label>
                      <input
                        id="workout-duration-hour"
                        name="workout-duration-hour"
                        class="workout-duration"
                        :class="{ errored: isDurationInvalid() }"
                        type="text"
                        inputmode="numeric"
                        placeholder="HH"
                        minlength="1"
                        maxlength="2"
                        pattern="^([0-1]?[0-9]|2[0-3])$"
                        required
                        @invalid="invalidateForm"
                        :disabled="loading"
                        v-model="workoutForm.workoutDurationHours"
                      />
                      :
                      <label
                        for="workout-duration-minutes"
                        class="visually-hidden"
                      >
                        {{ $t('common.MINUTES', 0) }}
                      </label>
                      <input
                        id="workout-duration-minutes"
                        name="workout-duration-minutes"
                        class="workout-duration"
                        :class="{ errored: isDurationInvalid() }"
                        type="text"
                        inputmode="numeric"
                        pattern="^([0-5][0-9])$"
                        minlength="2"
                        maxlength="2"
                        placeholder="MM"
                        required
                        @invalid="invalidateForm"
                        :disabled="loading"
                        v-model="workoutForm.workoutDurationMinutes"
                      />
                      :
                      <label
                        for="workout-duration-seconds"
                        class="visually-hidden"
                      >
                        {{ $t('common.SECONDS', 0) }}
                      </label>
                      <input
                        id="workout-duration-seconds"
                        name="workout-duration-seconds"
                        class="workout-duration"
                        :class="{ errored: isDurationInvalid() }"
                        type="text"
                        inputmode="numeric"
                        pattern="^([0-5][0-9])$"
                        minlength="2"
                        maxlength="2"
                        placeholder="SS"
                        required
                        @invalid="invalidateForm"
                        :disabled="loading"
                        v-model="workoutForm.workoutDurationSeconds"
                      />
                    </div>
                  </div>
                </div>
                <div class="workout-data">
                  <div class="form-item">
                    <label>
                      {{ $t('workouts.DISTANCE') }} ({{
                        authUser.imperial_units ? 'mi' : 'km'
                      }})*:
                    </label>
                    <input
                      :class="{ errored: isDistanceInvalid() }"
                      name="workout-distance"
                      type="number"
                      max="999.999"
                      min="0"
                      step="0.001"
                      required
                      @invalid="invalidateForm"
                      :disabled="loading"
                      v-model="workoutForm.workoutDistance"
                    />
                  </div>
                  <div class="form-item">
                    <label>
                      {{ $t('workouts.ASCENT') }} ({{
                        authUser.imperial_units ? 'ft' : 'm'
                      }}):
                    </label>
                    <input
                      :class="{ errored: isElevationInvalid() }"
                      name="workout-ascent"
                      type="number"
                      max="99999.999"
                      min="0"
                      step="0.001"
                      @invalid="invalidateForm"
                      :disabled="loading"
                      v-model="workoutForm.workoutAscent"
                    />
                  </div>
                  <div class="form-item">
                    <label>
                      {{ $t('workouts.DESCENT') }} ({{
                        authUser.imperial_units ? 'ft' : 'm'
                      }}):
                    </label>
                    <input
                      :class="{ errored: isElevationInvalid() }"
                      name="workout-descent"
                      type="number"
                      max="99999.999"
                      min="0"
                      step="0.001"
                      @invalid="invalidateForm"
                      :disabled="loading"
                      v-model="workoutForm.workoutDescent"
                    />
                  </div>
                </div>
              </div>
              <div class="form-item" v-if="equipments">
                <label for="workout-equipment">
                  {{ $t('equipments.EQUIPMENT', 1) }}:
                </label>
                <select
                  id="workout-equipment"
                  @invalid="invalidateForm"
                  :disabled="loading"
                  v-model="workoutForm.equipment_id"
                >
                  <option value="">{{ $t('equipments.NO_EQUIPMENTS') }}</option>
                  <option
                    v-for="equipment in equipmentsForSelect"
                    :value="equipment.id"
                    :key="equipment.id"
                  >
                    {{ equipment.label }}
                  </option>
                </select>
              </div>
              <div class="form-item">
                <label for="workout_visibility">
                  {{ $t('visibility_levels.WORKOUT_VISIBILITY') }}:
                </label>
                <select
                  id="workout_visibility"
                  v-model="workoutForm.workoutVisibility"
                  :disabled="loading"
                  @change="updateAnalysisAndMapVisibility"
                >
                  <option
                    v-for="level in visibilityLevels"
                    :value="level"
                    :key="level"
                  >
                    {{ $t(`visibility_levels.LEVELS.${level}`) }}
                  </option>
                </select>
              </div>
              <div class="form-item" v-if="withGpx">
                <label for="analysis_visibility">
                  {{ $t('visibility_levels.ANALYSIS_VISIBILITY') }}:
                </label>
                <select
                  id="analysis_visibility"
                  v-model="workoutForm.analysisVisibility"
                  @change="updateMapVisibility"
                  :disabled="loading"
                >
                  <option
                    v-for="level in analysisVisibilityLevels"
                    :value="level"
                    :key="level"
                  >
                    {{ $t(`visibility_levels.LEVELS.${level}`) }}
                  </option>
                </select>
              </div>
              <div class="form-item" v-if="withGpx">
                <label for="map_visibility">
                  {{ $t('visibility_levels.MAP_VISIBILITY') }}:
                </label>
                <select
                  id="map_visibility"
                  v-model="workoutForm.mapVisibility"
                  :disabled="loading"
                >
                  <option
                    v-for="level in mapVisibilityLevels"
                    :value="level"
                    :key="level"
                  >
                    {{ $t(`visibility_levels.LEVELS.${level}`) }}
                  </option>
                </select>
              </div>
              <div class="form-item" v-if="isCreation">
                <label for="description">
                  {{ $t('workouts.DESCRIPTION') }}:
                </label>
                <CustomTextArea
                  name="description"
                  :input="workoutForm.description"
                  :disabled="loading"
                  :charLimit="10000"
                  :rows="5"
                  @updateValue="updateDescription"
                />
                <div class="field-help" v-if="withGpx && isCreation">
                  <span class="info-box">
                    <i class="fa fa-info-circle" aria-hidden="true" />
                    {{ $t('workouts.DESCRIPTION_FIELD_HELP') }}
                  </span>
                </div>
              </div>
              <div class="form-item" v-if="isCreation">
                <label for="notes"> {{ $t('workouts.PRIVATE_NOTES') }}: </label>
                <CustomTextArea
                  name="notes"
                  :input="workoutForm.notes"
                  :disabled="loading"
                  @updateValue="updateNotes"
                />
                <div class="field-help" v-if="isCreation">
                  <span class="info-box">
                    <i class="fa fa-info-circle" aria-hidden="true" />
                    {{ $t('workouts.PRIVATE_NOTES_FIELD_HELP') }}
                  </span>
                </div>
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

<script setup lang="ts">
  import { computed, reactive, ref, toRefs, watch, onMounted } from 'vue'
  import type { ComputedRef, Ref } from 'vue'
  import { useI18n } from 'vue-i18n'
  import { useRouter } from 'vue-router'

  import useApp from '@/composables/useApp'
  import {
    EQUIPMENTS_STORE,
    ROOT_STORE,
    WORKOUTS_STORE,
  } from '@/store/constants'
  import type { IEquipment } from '@/types/equipments'
  import type { ICustomTextareaData } from '@/types/forms'
  import type { ISport, ITranslatedSport } from '@/types/sports'
  import type { IAuthUserProfile, TVisibilityLevels } from '@/types/user'
  import type { IWorkout, IWorkoutForm } from '@/types/workouts'
  import { useStore } from '@/use/useStore'
  import { formatWorkoutDate, getDateWithTZ } from '@/utils/dates'
  import { getEquipments } from '@/utils/equipments'
  import { getReadableFileSizeAsText } from '@/utils/files'
  import { translateSports } from '@/utils/sports'
  import { convertDistance } from '@/utils/units'
  import {
    getAllVisibilityLevels,
    getVisibilityLevels,
    getUpdatedVisibility,
  } from '@/utils/visibility_levels'

  interface Props {
    authUser: IAuthUserProfile
    sports: ISport[]
    isCreation?: boolean
    loading?: boolean
    workout?: IWorkout
  }
  const props = withDefaults(defineProps<Props>(), {
    isCreation: false,
    loading: false,
    workout: () => ({}) as IWorkout,
  })
  const { authUser, workout, isCreation, loading } = toRefs(props)

  const router = useRouter()
  const store = useStore()
  const { t } = useI18n()

  const { appConfig, errorMessages } = useApp()

  let gpxFile: File | null = null

  const workoutForm = reactive({
    sport_id: '',
    title: '',
    notes: '',
    workoutDate: '',
    workoutTime: '',
    workoutDurationHours: '',
    workoutDurationMinutes: '',
    workoutDurationSeconds: '',
    workoutDistance: '',
    workoutAscent: '',
    workoutDescent: '',
    equipment_id: '',
    description: '',
    mapVisibility: authUser.value.map_visibility,
    analysisVisibility: authUser.value.analysis_visibility,
    workoutVisibility: authUser.value.workouts_visibility,
  })
  const withGpx: Ref<boolean> = ref(
    workout.value.id && workout.value.with_gpx ? true : isCreation.value
  )
  const formErrors: Ref<boolean> = ref(false)
  const payloadErrorMessages: Ref<string[]> = ref([])

  const translatedSports: ComputedRef<ITranslatedSport[]> = computed(() =>
    translateSports(
      props.sports,
      t,
      'is_active_for_user',
      workout.value.id ? [workout.value.sport_id] : []
    )
  )
  const fileSizeLimit: ComputedRef<string> = computed(() =>
    appConfig.value.max_single_file_size
      ? getReadableFileSizeAsText(appConfig.value.max_single_file_size)
      : ''
  )
  const fileLimitImport: ComputedRef<number> = computed(
    () => appConfig.value.file_limit_import
  )
  const fileSyncLimitImport: ComputedRef<number> = computed(
    () => appConfig.value.file_sync_limit_import
  )
  const zipSizeLimit: ComputedRef<string> = computed(() =>
    appConfig.value.max_zip_file_size
      ? getReadableFileSizeAsText(appConfig.value.max_zip_file_size)
      : ''
  )
  const asyncUploadEnabled: ComputedRef<boolean> = computed(
    () =>
      appConfig.value.file_sync_limit_import !=
      appConfig.value.file_limit_import
  )
  const equipments: ComputedRef<IEquipment[]> = computed(
    () => store.getters[EQUIPMENTS_STORE.GETTERS.EQUIPMENTS]
  )
  const selectedSport: ComputedRef<ITranslatedSport | null> = computed(() =>
    workoutForm.sport_id
      ? translatedSports.value.filter((s) => s.id === +workoutForm.sport_id)[0]
      : null
  )
  const equipmentsForSelect: ComputedRef<IEquipment[]> = computed(() =>
    equipments.value
      ? getEquipments(
          equipments.value,
          t,
          isCreation.value ? 'is_active' : 'withIncludedIds',
          selectedSport.value,
          isCreation.value
            ? []
            : // eslint-disable-next-line @typescript-eslint/ban-ts-comment
              // @ts-ignore
              workout.value.equipments.map((e) => e.id)
        )
      : []
  )
  const visibilityLevels: ComputedRef<TVisibilityLevels[]> = computed(() =>
    getAllVisibilityLevels()
  )
  const analysisVisibilityLevels: ComputedRef<TVisibilityLevels[]> = computed(
    () => getVisibilityLevels(workoutForm.workoutVisibility)
  )
  const mapVisibilityLevels: ComputedRef<TVisibilityLevels[]> = computed(() =>
    getVisibilityLevels(workoutForm.analysisVisibility)
  )

  function updateNotes(textareaData: ICustomTextareaData) {
    workoutForm.notes = textareaData.value
  }
  function updateDescription(textareaData: ICustomTextareaData) {
    workoutForm.description = textareaData.value
  }
  function updateWithGpx() {
    withGpx.value = !withGpx.value
    formErrors.value = false
  }
  function updateFile(event: Event) {
    if ((event.target as HTMLInputElement).files) {
      gpxFile = ((event.target as HTMLInputElement).files as FileList)[0]
    }
  }
  function formatWorkoutForm(workout: IWorkout) {
    workoutForm.sport_id = `${workout.sport_id}`
    workoutForm.title = workout.title
    workoutForm.description = workout.description
    workoutForm.notes = workout.notes
    workoutForm.equipment_id =
      workout.equipments.length > 0 && 'id' in workout.equipments[0]
        ? `${workout.equipments[0].id}`
        : ''
    workoutForm.workoutVisibility = workout.workout_visibility
      ? workout.workout_visibility
      : 'private'
    workoutForm.analysisVisibility = workout.analysis_visibility
      ? workout.analysis_visibility
      : 'private'
    workoutForm.mapVisibility = workout.map_visibility
      ? workout.map_visibility
      : 'private'
    if (!workout.with_gpx) {
      const workoutDateTime = formatWorkoutDate(
        getDateWithTZ(workout.workout_date, props.authUser.timezone),
        'yyyy-MM-dd'
      )
      if (workout.duration) {
        const [hours, minutes, seconds] = workout.duration.split(':')
        workoutForm.workoutDurationHours = hours
        workoutForm.workoutDurationMinutes = minutes
        workoutForm.workoutDurationSeconds = seconds
      }
      if (workout.distance) {
        workoutForm.workoutDistance = `${
          authUser.value.imperial_units
            ? convertDistance(workout.distance, 'km', 'mi', 3)
            : parseFloat(workout.distance.toFixed(3))
        }`
      }
      workoutForm.workoutDate = workoutDateTime.workout_date
      workoutForm.workoutTime = workoutDateTime.workout_time
      workoutForm.workoutAscent =
        workout.ascent === null
          ? ''
          : `${
              authUser.value.imperial_units
                ? convertDistance(workout.ascent, 'm', 'ft', 2)
                : parseFloat(workout.ascent.toFixed(2))
            }`
      workoutForm.workoutDescent =
        workout.descent === null
          ? ''
          : `${
              authUser.value.imperial_units
                ? convertDistance(workout.descent, 'm', 'ft', 2)
                : parseFloat(workout.descent.toFixed(2))
            }`
    }
  }
  function isDistanceInvalid() {
    return payloadErrorMessages.value.includes('workouts.INVALID_DISTANCE')
  }
  function isDurationInvalid() {
    return payloadErrorMessages.value.includes('workouts.INVALID_DURATION')
  }
  function isElevationInvalid() {
    return payloadErrorMessages.value.includes(
      'workouts.INVALID_ASCENT_OR_DESCENT'
    )
  }
  function formatPayload(payload: IWorkoutForm) {
    payloadErrorMessages.value = []
    payload.duration =
      +workoutForm.workoutDurationHours * 3600 +
      +workoutForm.workoutDurationMinutes * 60 +
      +workoutForm.workoutDurationSeconds
    if (payload.duration <= 0) {
      payloadErrorMessages.value.push('workouts.INVALID_DURATION')
    }
    payload.distance = authUser.value.imperial_units
      ? convertDistance(+workoutForm.workoutDistance, 'mi', 'km', 3)
      : +workoutForm.workoutDistance
    if (payload.distance <= 0) {
      payloadErrorMessages.value.push('workouts.INVALID_DISTANCE')
    }
    payload.workout_date = `${workoutForm.workoutDate} ${workoutForm.workoutTime}`
    payload.ascent =
      workoutForm.workoutAscent === ''
        ? null
        : authUser.value.imperial_units
          ? convertDistance(+workoutForm.workoutAscent, 'ft', 'm', 3)
          : +workoutForm.workoutAscent
    payload.descent =
      workoutForm.workoutDescent === ''
        ? null
        : authUser.value.imperial_units
          ? convertDistance(+workoutForm.workoutDescent, 'ft', 'm', 3)
          : +workoutForm.workoutDescent
    if (
      (payload.ascent !== null && payload.descent === null) ||
      (payload.ascent === null && payload.descent !== null)
    ) {
      payloadErrorMessages.value.push('workouts.INVALID_ASCENT_OR_DESCENT')
    }
    payload.workout_visibility = workoutForm.workoutVisibility
  }
  function updateWorkout() {
    const payload: IWorkoutForm = {
      sport_id: +workoutForm.sport_id,
      description: workoutForm.description,
      notes: workoutForm.notes,
      equipment_ids:
        workoutForm.equipment_id &&
        equipmentsForSelect.value.find((e) => e.id === workoutForm.equipment_id)
          ? [workoutForm.equipment_id]
          : [],
      title: workoutForm.title,
      workout_visibility: workoutForm.workoutVisibility,
    }
    if (props.workout.id) {
      if (props.workout.with_gpx) {
        payload.analysis_visibility = workoutForm.analysisVisibility
        payload.map_visibility = workoutForm.mapVisibility
      } else {
        formatPayload(payload)
      }
      if (payloadErrorMessages.value.length > 0) {
        store.commit(
          ROOT_STORE.MUTATIONS.SET_ERROR_MESSAGES,
          payloadErrorMessages.value
        )
      } else {
        store.dispatch(WORKOUTS_STORE.ACTIONS.EDIT_WORKOUT, {
          workoutId: props.workout.id,
          data: payload,
        })
      }
    } else {
      if (withGpx.value) {
        if (!gpxFile) {
          const errorMessage = 'workouts.NO_FILE_PROVIDED'
          store.commit(ROOT_STORE.MUTATIONS.SET_ERROR_MESSAGES, errorMessage)
          return
        }
        payload.file = gpxFile
        payload.analysis_visibility = workoutForm.analysisVisibility
        payload.map_visibility = workoutForm.mapVisibility
        store.dispatch(WORKOUTS_STORE.ACTIONS.ADD_WORKOUT, payload)
      } else {
        formatPayload(payload)
        if (payloadErrorMessages.value.length > 0) {
          store.commit(
            ROOT_STORE.MUTATIONS.SET_ERROR_MESSAGES,
            payloadErrorMessages.value
          )
        } else {
          store.dispatch(
            WORKOUTS_STORE.ACTIONS.ADD_WORKOUT_WITHOUT_GPX,
            payload
          )
        }
      }
    }
  }
  function onCancel() {
    if (props.workout.id) {
      router.push({
        name: 'Workout',
        params: { workoutId: props.workout.id },
      })
    } else if (window.history.length > 1) {
      router.go(-1)
    } else {
      router.push('/')
    }
  }
  function invalidateForm() {
    formErrors.value = true
  }
  function updateAnalysisAndMapVisibility() {
    workoutForm.analysisVisibility = getUpdatedVisibility(
      workoutForm.analysisVisibility,
      workoutForm.workoutVisibility
    )
    updateMapVisibility()
  }
  function updateMapVisibility() {
    workoutForm.mapVisibility = getUpdatedVisibility(
      workoutForm.mapVisibility,
      workoutForm.analysisVisibility
    )
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
  watch(
    () => selectedSport.value,
    (newSport: ISport | null) => {
      if (isCreation.value) {
        workoutForm.equipment_id =
          newSport?.default_equipments &&
          newSport?.default_equipments.length > 0
            ? `${newSport.default_equipments[0].id}`
            : ''
      }
    }
  )
  watch(
    () => authUser.value,
    (newAuthUser: IAuthUserProfile) => {
      if (newAuthUser && isCreation) {
        workoutForm.workoutVisibility = newAuthUser.workouts_visibility
        workoutForm.analysisVisibility = newAuthUser.analysis_visibility
        workoutForm.mapVisibility = newAuthUser.map_visibility
      }
    }
  )

  onMounted(() => {
    let element
    if (props.workout.id) {
      formatWorkoutForm(props.workout)
      element = document.getElementById('sport')
    } else {
      element = document.getElementById('withGpx')
    }
    if (element) {
      element.focus()
    }
  })
</script>

<style lang="scss" scoped>
  @use '~@/scss/vars.scss' as *;

  #workout-edition {
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
            label {
              text-transform: lowercase;
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
              padding: $default-padding * 0.5 $default-padding
                $default-padding * 0.25;

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
            padding: $default-padding $default-padding * 0.5 0;
            button {
              margin: $default-margin * 0.5;
            }
          }

          .files-info-box {
            margin-top: $default-margin;
            padding: 0 $default-padding;
            .files-help {
              display: flex;
              justify-content: space-around;
              padding: $default-padding * 0.75 $default-padding;

              div {
                display: flex;

                ul {
                  margin: 0;
                  padding: 0 $default-padding * 2;
                }
              }

              @media screen and (max-width: $medium-limit) {
                flex-direction: column;
                div {
                  flex-direction: column;
                }
              }
            }
            .weather-info {
              padding: 0 $default-padding $default-padding;
            }
          }

          .field-help {
            display: flex;
            margin-top: $default-margin * 0.5;
          }

          .workout-data {
            display: flex;
            flex-direction: row;
            justify-content: space-between;
            .form-item {
              width: 30%;
            }

            @media screen and (max-width: $medium-limit) {
              flex-direction: column;
              .form-item {
                width: initial;
              }
            }
          }
        }
      }
    }

    @media screen and (max-width: $small-limit) {
      margin-bottom: 0;
      &.center-form {
        margin: 50px auto;
      }

      &.with-margin {
        margin-top: 0;
      }
    }

    .errored {
      outline: 2px solid var(--input-error-color);
    }
  }
</style>
