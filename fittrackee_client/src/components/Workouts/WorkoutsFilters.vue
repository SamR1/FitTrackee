<template>
  <div class="workouts-filters">
    <div class="box">
      <form @submit.prevent class="form">
        <div class="form-all-items">
          <div class="form-items-group">
            <div class="form-item">
              <label for="from"> {{ $t('workouts.FROM') }}: </label>
              <input
                id="from"
                name="from"
                type="date"
                :disabled="geocodeLoading"
                :value="$route.query.from"
                @change="handleFilterChange"
              />
            </div>
            <div class="form-item">
              <label for="to"> {{ $t('workouts.TO') }}: </label>
              <input
                id="to"
                name="to"
                type="date"
                :disabled="geocodeLoading"
                :value="$route.query.to"
                @change="handleFilterChange"
              />
            </div>
            <div class="form-item">
              <label for="sport_id"> {{ $t('workouts.SPORT', 1) }}:</label>
              <select
                id="sport_id"
                name="sport_id"
                :disabled="geocodeLoading"
                :value="sportId"
                @change="handleSportChange"
                @keyup.enter="onFilter"
              >
                <option value="" />
                <option
                  v-for="sport in translatedSports.filter((s) =>
                    authUser.sports_list.includes(s.id)
                  )"
                  :value="sport.id"
                  :key="sport.id"
                >
                  {{ sport.translatedLabel }}
                </option>
              </select>
            </div>
            <div class="form-item form-item-equipment">
              <label> {{ $t('equipments.EQUIPMENT', 1) }}:</label>
              <select
                name="equipment_id"
                :disabled="geocodeLoading"
                :value="$route.query.equipment_id"
                @change="handleFilterChange"
                @keyup.enter="onFilter"
              >
                <option value="" />
                <option
                  v-if="Object.keys(equipmentsWithWorkouts).length == 0"
                  value=""
                  disabled
                  selected
                >
                  {{ $t('equipments.NO_EQUIPMENTS') }}
                </option>
                <template v-if="Object.keys(equipmentsWithWorkouts).length > 0">
                  <option value="none">
                    {{ $t('equipments.WITHOUT_EQUIPMENTS') }}
                  </option>
                  <option disabled>---</option>
                </template>
                <optgroup
                  v-for="equipmentTypeLabel in Object.keys(
                    equipmentsWithWorkouts
                  ).sort()"
                  :label="equipmentTypeLabel"
                  :key="equipmentTypeLabel"
                >
                  <option
                    v-for="equipment in equipmentsWithWorkouts[
                      equipmentTypeLabel
                    ].sort(sortEquipments)"
                    :value="equipment.id"
                    :key="equipment.id"
                  >
                    {{ equipment.label }}
                  </option>
                </optgroup>
              </select>
            </div>
            <div class="form-item form-item-text">
              <label for="title"> {{ $t('workouts.TITLE', 1) }}:</label>
              <div class="form-inputs-group">
                <input
                  id="title"
                  class="text"
                  name="title"
                  :disabled="geocodeLoading"
                  :value="$route.query.title"
                  @change="handleFilterChange"
                  placeholder=""
                  type="text"
                  @keyup.enter="onFilter"
                />
              </div>
            </div>
          </div>
          <div class="form-items-group">
            <div class="form-item form-item-text">
              <label for="description">
                {{ $t('workouts.DESCRIPTION') }}:
              </label>
              <div class="form-inputs-group">
                <input
                  id="description"
                  class="text"
                  name="description"
                  :disabled="geocodeLoading"
                  :value="$route.query.description"
                  @change="handleFilterChange"
                  placeholder=""
                  type="text"
                  @keyup.enter="onFilter"
                />
              </div>
            </div>
            <div class="form-item form-item-text">
              <label for="notes"> {{ $t('workouts.NOTES') }}:</label>
              <div class="form-inputs-group">
                <input
                  id="notes"
                  class="text"
                  name="notes"
                  :value="$route.query.notes"
                  @change="handleFilterChange"
                  placeholder=""
                  type="text"
                  @keyup.enter="onFilter"
                />
              </div>
            </div>
            <div class="form-item form-item-text">
              <label for="location">{{ $t('workouts.LOCATION') }}:</label>
              <LocationsDropdown
                :location="location"
                @updateCoordinates="handleLocationChange"
                @keyup.enter="onFilter"
              />
            </div>
            <div class="form-item form-item-text">
              <label for="radius">
                {{ $t('workouts.RADIUS') }} ({{ toUnit }}):</label
              >
              <div class="form-inputs-group">
                <input
                  id="radius"
                  class="text"
                  :class="{ disabled: !location }"
                  name="radius"
                  :disabled="geocodeLoading"
                  :readonly="!location"
                  :tabindex="location ? 0 : -1"
                  :value="radius"
                  placeholder=""
                  type="number"
                  @change="handleFilterChange"
                  @keyup.enter="onFilter"
                />
              </div>
            </div>

            <div class="form-item form-item-text">
              <label for="workout_visibility">
                {{ $t('visibility_levels.WORKOUT_VISIBILITY').toLowerCase() }}:
              </label>
              <select
                id="workout_visibility"
                name="workout_visibility"
                :disabled="geocodeLoading"
                :value="$route.query.workout_visibility"
                @change="handleFilterChange"
                @keyup.enter="onFilter"
              >
                <option value="" />
                <option
                  v-for="level in visibilityLevels"
                  :value="level"
                  :key="level"
                >
                  {{ $t(`visibility_levels.LEVELS.${level}`) }}
                </option>
              </select>
            </div>
          </div>

          <div class="additional-filters">
            <div @click="toggleMoreFilters" class="additional-filters-btn">
              <button class="transparent">
                <i
                  :class="`fa fa-caret-${displayMoreFilters ? 'up' : 'down'}`"
                  aria-hidden="true"
                />
                <span>
                  {{
                    $t(
                      `workouts.${displayMoreFilters ? 'HIDE' : 'DISPLAY_MORE'}_FILTERS`
                    )
                  }}
                </span>
              </button>
            </div>
            <div v-if="displayMoreFilters" class="additional-filters-filters">
              <div class="form-items-group">
                <div class="form-item">
                  <label> {{ $t('workouts.DISTANCE') }} ({{ toUnit }}): </label>
                  <div class="form-inputs-group">
                    <input
                      name="distance_from"
                      type="number"
                      min="0"
                      step="0.1"
                      :disabled="geocodeLoading"
                      :value="$route.query.distance_from"
                      @change="handleFilterChange"
                      @keyup.enter="onFilter"
                    />
                    <span>{{ $t('workouts.TO') }}</span>
                    <input
                      name="distance_to"
                      type="number"
                      min="0"
                      step="0.1"
                      :disabled="geocodeLoading"
                      :value="$route.query.distance_to"
                      @change="handleFilterChange"
                      @keyup.enter="onFilter"
                    />
                  </div>
                </div>
                <div class="form-item">
                  <label> {{ $t('workouts.DURATION') }}: </label>
                  <div class="form-inputs-group">
                    <label for="duration_from" class="visually-hidden">
                      {{ $t('workouts.FROM') }}
                    </label>
                    <input
                      id="duration_from"
                      name="duration_from"
                      :disabled="geocodeLoading"
                      :value="$route.query.duration_from"
                      @change="handleFilterChange"
                      pattern="^([0-9]*[0-9]):([0-5][0-9])$"
                      placeholder="hh:mm"
                      type="text"
                      @keyup.enter="onFilter"
                    />
                    <span>{{ $t('workouts.TO') }}</span>
                    <label for="duration_to" class="visually-hidden">
                      {{ $t('workouts.TO') }}
                    </label>
                    <input
                      id="duration_to"
                      name="duration_to"
                      :disabled="geocodeLoading"
                      :value="$route.query.duration_to"
                      @change="handleFilterChange"
                      pattern="^([0-9]*[0-9]):([0-5][0-9])$"
                      placeholder="hh:mm"
                      type="text"
                      @keyup.enter="onFilter"
                    />
                  </div>
                </div>
              </div>

              <div class="form-items-group">
                <div class="form-item">
                  <label>
                    {{ $t('workouts.AVE_SPEED') }} ({{ toUnit }}/h):
                  </label>
                  <div class="form-inputs-group">
                    <input
                      min="0"
                      name="ave_speed_from"
                      :disabled="geocodeLoading"
                      :value="$route.query.ave_speed_from"
                      @change="handleFilterChange"
                      step="0.1"
                      type="number"
                      @keyup.enter="onFilter"
                    />
                    <span>{{ $t('workouts.TO') }}</span>
                    <input
                      min="0"
                      name="ave_speed_to"
                      :disabled="geocodeLoading"
                      :value="$route.query.ave_speed_to"
                      @change="handleFilterChange"
                      step="0.1"
                      type="number"
                      @keyup.enter="onFilter"
                    />
                  </div>
                </div>
                <div class="form-item">
                  <label>
                    {{ $t('workouts.MAX_SPEED') }} ({{ toUnit }}/h):
                  </label>
                  <div class="form-inputs-group">
                    <input
                      min="0"
                      name="max_speed_from"
                      :disabled="geocodeLoading"
                      :value="$route.query.max_speed_from"
                      @change="handleFilterChange"
                      step="0.1"
                      type="number"
                      @keyup.enter="onFilter"
                    />
                    <span>{{ $t('workouts.TO') }}</span>
                    <input
                      min="0"
                      name="max_speed_to"
                      :disabled="geocodeLoading"
                      :value="$route.query.max_speed_to"
                      @change="handleFilterChange"
                      step="0.1"
                      type="number"
                      @keyup.enter="onFilter"
                    />
                  </div>
                </div>
              </div>

              <div class="form-items-group">
                <div class="form-item">
                  <label>
                    {{ $t('workouts.AVE_PACE') }} (min/{{ toUnit }}):
                  </label>
                  <div class="form-inputs-group">
                    <input
                      min="0"
                      name="ave_pace_from"
                      :disabled="disablePaceInputs"
                      :value="$route.query.ave_pace_from"
                      @change="handleFilterChange"
                      pattern="^([0-9]*[0-9]):([0-5][0-9])$"
                      placeholder="mm:ss"
                      type="text"
                      @keyup.enter="onFilter"
                    />
                    <span>{{ $t('workouts.TO') }}</span>
                    <input
                      min="0"
                      name="ave_pace_to"
                      :disabled="disablePaceInputs"
                      :value="$route.query.ave_pace_to"
                      @change="handleFilterChange"
                      pattern="^([0-9]*[0-9]):([0-5][0-9])$"
                      placeholder="mm:ss"
                      type="text"
                      @keyup.enter="onFilter"
                    />
                  </div>
                </div>
                <div class="form-item">
                  <label>
                    {{ $t('workouts.MAX_PACE') }} (min/{{ toUnit }}):
                  </label>
                  <div class="form-inputs-group">
                    <input
                      min="0"
                      name="max_pace_from"
                      :disabled="disablePaceInputs"
                      :value="$route.query.max_pace_from"
                      @change="handleFilterChange"
                      pattern="^([0-9]*[0-9]):([0-5][0-9])$"
                      placeholder="mm:ss"
                      type="text"
                      @keyup.enter="onFilter"
                    />
                    <span>{{ $t('workouts.TO') }}</span>
                    <input
                      min="0"
                      name="max_pace_to"
                      :disabled="disablePaceInputs"
                      :value="$route.query.max_pace_to"
                      @change="handleFilterChange"
                      pattern="^([0-9]*[0-9]):([0-5][0-9])$"
                      placeholder="mm:ss"
                      type="text"
                      @keyup.enter="onFilter"
                    />
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="form-button">
          <button
            type="submit"
            class="confirm"
            @click="onFilter"
            :disabled="geocodeLoading"
          >
            {{ $t('buttons.FILTER') }}
          </button>
          <button
            class="confirm"
            @click="onClearFilter"
            :disabled="geocodeLoading"
          >
            {{ $t('buttons.CLEAR_FILTER') }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
  import { computed, toRefs, watch, onMounted, onBeforeMount, ref } from 'vue'
  import type { ComputedRef, Ref } from 'vue'
  import { useI18n } from 'vue-i18n'
  import { useRoute, useRouter } from 'vue-router'
  import type { LocationQuery } from 'vue-router'
  import { useStore } from 'vuex'

  import LocationsDropdown from '@/components/Workouts/LocationsDropdown.vue'
  import useApp from '@/composables/useApp.ts'
  import { EQUIPMENTS_STORE, WORKOUTS_STORE } from '@/store/constants'
  import type { IEquipment } from '@/types/equipments'
  import type { ITranslatedSport } from '@/types/sports'
  import type { IAuthUserProfile, TVisibilityLevels } from '@/types/user'
  import { sortEquipments } from '@/utils/equipments'
  import { getLocationFromOsmId } from '@/utils/geocode.ts'
  import { sportsWithPace } from '@/utils/sports.ts'
  import { units } from '@/utils/units'
  import { getAllVisibilityLevels } from '@/utils/visibility_levels.ts'

  interface Props {
    authUser: IAuthUserProfile
    translatedSports: ITranslatedSport[]
  }
  const props = defineProps<Props>()
  const { authUser, translatedSports } = toRefs(props)

  const emit = defineEmits(['filter', 'updateSportWithPace'])

  const route = useRoute()
  const router = useRouter()
  const store = useStore()
  const { t } = useI18n()

  const { appLanguage } = useApp()

  let params: LocationQuery = Object.assign({}, route.query)

  const toUnit: ComputedRef<string> = computed(() =>
    authUser.value.imperial_units ? units['km'].defaultTarget : 'km'
  )
  const equipmentsWithWorkouts: ComputedRef<Record<string, IEquipment[]>> =
    computed(() =>
      getEquipmentsFilters(store.getters[EQUIPMENTS_STORE.GETTERS.EQUIPMENTS])
    )
  const visibilityLevels: ComputedRef<TVisibilityLevels[]> = computed(() =>
    getAllVisibilityLevels()
  )
  const location: Ref<string> = ref('')
  const radius: Ref<string> = ref('')
  const geocodeLoading: ComputedRef<boolean> = computed(
    () => store.getters[WORKOUTS_STORE.GETTERS.GEOCODE_LOADING]
  )
  const sportId: Ref<string> = ref('')
  const disablePaceInputs: Ref<boolean> = ref(true)
  const displayMoreFilters: Ref<boolean> = ref(false)

  function handleFilterChange(event: Event) {
    const name = (event.target as HTMLInputElement).name
    const value = (event.target as HTMLInputElement).value
    if (value === '') {
      delete params[name]
    } else {
      params[name] = value
    }
    if (name === 'radius') {
      radius.value = value
    }
  }
  function handleLocationChange(newLocation: {
    coordinates: string
    display_name: string
    osm_id: string
  }) {
    if (newLocation.coordinates === '') {
      delete params.coordinates
      delete params.osm_id
      delete params.radius
      radius.value = ''
    } else {
      params.coordinates = newLocation.coordinates
      params.osm_id = newLocation.osm_id
      if (!radius.value) {
        params.radius = '10'
        radius.value = '10'
      }
    }
    location.value = newLocation.display_name || ''
  }
  function updateOrderBy(sportWithPace: boolean) {
    if (params.order_by === 'ave_speed' && sportWithPace) {
      params.order_by = 'ave_pace'
    }
    if (params.order_by === 'ave_pace' && !sportWithPace) {
      params.order_by = 'ave_speed'
    }
  }
  function handleSportChange(event: Event) {
    sportId.value = (event.target as HTMLInputElement).value
    let selectedSport = undefined
    if (sportId.value === '') {
      delete params.sport_id
      updateOrderBy(false)
    } else {
      params.sport_id = sportId.value
      selectedSport = translatedSports.value.find(
        (sport) => sport.id === +sportId.value
      )
    }
    if (selectedSport && sportsWithPace.includes(selectedSport.label)) {
      disablePaceInputs.value = false
      updateOrderBy(true)
    } else {
      delete params.ave_pace_from
      delete params.ave_pace_to
      delete params.max_pace_from
      delete params.max_pace_to
      disablePaceInputs.value = true
      updateOrderBy(false)
    }
  }
  function onFilter() {
    emit('filter')
    emit('updateSportWithPace', sportId.value)
    if ('page' in params) {
      params['page'] = '1'
    }
    router.push({ path: '/workouts', query: params })
  }
  function onClearFilter() {
    location.value = ''
    radius.value = ''
    sportId.value = ''
    emit('filter')
    router.push({ path: '/workouts', query: {} })
  }
  function getEquipmentsFilters(equipments: IEquipment[]) {
    const equipmentTypes: Record<string, IEquipment[]> = {}
    equipments
      .filter((e: IEquipment) => e.workouts_count > 0)
      .map((e) => {
        const equipmentTypeLabel = t(
          `equipment_types.${e.equipment_type.label}.LABEL`
        )
        if (!(equipmentTypeLabel in equipmentTypes)) {
          equipmentTypes[equipmentTypeLabel] = [e]
        } else {
          equipmentTypes[equipmentTypeLabel].push(e)
        }
      })
    return equipmentTypes
  }
  function toggleMoreFilters() {
    displayMoreFilters.value = !displayMoreFilters.value
  }

  watch(
    () => route.query,
    (newQuery) => {
      params = Object.assign({}, newQuery)
    }
  )

  onBeforeMount(async () => {
    if (route.query.osm_id) {
      const result = await getLocationFromOsmId(
        route.query.osm_id as string,
        appLanguage.value
      )
      if (result.display_name) {
        location.value = result.display_name
        radius.value = (route.query.radius as string) || ''
      }
    } else {
      location.value = ''
      radius.value = ''
    }
    if (route.query.sport_id) {
      sportId.value = route.query.sport_id as string
      const selectedSport = translatedSports.value.find(
        (sport) => sport.id === +sportId.value
      )
      disablePaceInputs.value = !(
        selectedSport && sportsWithPace.includes(selectedSport.label)
      )
    }
  })
  onMounted(() => {
    const filter = document.getElementById('from')
    if (filter) {
      filter.focus()
    }
  })
</script>

<style lang="scss" scoped>
  @use '~@/scss/vars.scss' as *;

  .workouts-filters {
    .form {
      .form-all-items {
        display: flex;
        flex-direction: column;
        padding-top: 0;

        .form-items-group {
          display: flex;
          flex-direction: column;
          padding: 0 $default-padding * 0.5;

          .form-item {
            display: flex;
            flex-direction: column;

            .form-inputs-group {
              display: flex;
              flex-direction: row;
              justify-content: space-around;
              align-items: center;

              input {
                width: 34%;
              }
              span {
                padding: $default-padding * 0.5;
              }
            }

            input {
              height: 16px;
            }

            select {
              height: 38px;
              padding: 0 $default-padding * 0.5;
            }
          }
          .form-item-text {
            input.text {
              width: 100%;
            }
          }
        }
      }
    }

    .form-button {
      display: flex;
      justify-content: center;
      flex-wrap: wrap;
      margin: 0 $default-margin * 0.5;

      button {
        margin-top: $default-margin;
        width: 100%;
      }
    }

    .disabled {
      pointer-events: none;
      background-color: var(--disabled-radius-input);
      border-color: var(--disabled-radius-border);
    }

    .additional-filters {
      display: flex;
      flex-direction: column;
      .additional-filters-btn {
        button {
          display: flex;
          align-items: center;
          gap: $default-padding * 0.5;
          padding-left: $default-padding;
          font-weight: bold;
        }
      }
      .additional-filters-filters {
        display: flex;
        flex-direction: column;
      }
    }

    @media screen and (max-width: $medium-limit) {
      .form {
        .form-all-items {
          flex-direction: row;
          .form-items-group {
            margin-top: 20px;
            padding: 0 $default-padding * 0.5;

            .form-item {
              max-width: 205px;
              label,
              span {
                font-size: 0.9em;
              }

              .form-inputs-group {
                flex-direction: column;
                justify-content: normal;
                padding: 0;

                input,
                select {
                  width: 90%;
                }
                span {
                  padding: 0;
                }
              }
            }

            .form-item-text {
              padding-top: 0;
            }
          }

          .additional-filters {
            .additional-filters-filters {
              flex-direction: row;
              gap: $default-padding;
              .form-items-group {
                margin-top: 0;
              }
              label {
                height: 40px;
                word-break: break-word;
              }
              .form-item {
                width: 100%;
              }
            }
          }
        }
      }

      .form-button {
        flex-wrap: initial;
        button {
          margin: $default-padding $default-padding * 0.5;
          width: 100%;
        }
      }
    }
    @media screen and (max-width: $small-limit) {
      .form {
        .form-all-items {
          flex-direction: column;
          padding-top: 0;

          .form-items-group {
            margin-top: 0;
            .form-item {
              max-width: initial;
              label {
                font-size: 1em;
              }

              .form-inputs-group {
                flex-direction: row;
                justify-content: space-around;
                align-items: center;

                input {
                  width: 50%;
                }

                span {
                  padding: $default-padding * 0.5;
                }
              }
            }
            .form-item-text {
              input.text {
                width: 100%;
              }
            }
          }
        }
      }
      .additional-filters {
        .additional-filters-filters {
          flex-direction: column !important;
          .form-item {
            width: 100% !important;
          }

          label {
            height: initial !important;
          }
        }
      }
      .form-button {
        flex-wrap: initial;
        button {
          margin: $default-padding $default-padding * 0.5;
        }
      }
    }

    @media screen and (max-width: $x-small-limit) {
      .form-button {
        flex-wrap: wrap;
      }
    }
  }
</style>
