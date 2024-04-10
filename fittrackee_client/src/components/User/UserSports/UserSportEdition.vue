<template>
  <div id="sport-edition" v-if="sport">
    <form
      :class="{ errors: formErrors }"
      @submit.prevent="updateSportPreferences"
    >
      <div class="form-items">
        <div class="form-item">
          <label for="sport-label">
            {{ capitalize($t('workouts.SPORT', 1)) }}
          </label>
          {{ sport.translatedLabel }}
        </div>
        <div class="form-item">
          <label for="sport-color">
            {{ capitalize($t('user.PROFILE.SPORT.COLOR')) }}
          </label>
          <input
            id="sport-color"
            name="sport-color"
            class="sport-color"
            type="color"
            required
            v-model="sportPayload.color"
            :disabled="loading"
            @invalid="invalidateForm"
          />
        </div>
        <div class="form-item">
          <label for="sport-threshold">
            {{ capitalize($t('user.PROFILE.SPORT.STOPPED_SPEED_THRESHOLD')) }}
            ({{ `${authUser.imperial_units ? 'mi' : 'km'}/h` }})*
          </label>
          <input
            id="sport-threshold"
            name="sport-threshold"
            class="threshold-input"
            type="number"
            min="0"
            step="0.1"
            required
            v-model="sportPayload.stopped_speed_threshold"
            :disabled="loading"
            @invalid="invalidateForm"
          />
        </div>
        <div class="form-item-checkbox">
          <label for="equipment-active">
            {{ capitalize($t('common.ACTIVE')) }}
          </label>
          <input
            type="checkbox"
            :checked="sport.is_active_for_user"
            @change="updateIsActive"
            :disabled="loading"
          />
        </div>
        <div class="form-item">
          <label for="sport-default-equipment">
            {{ $t('user.PROFILE.SPORT.DEFAULT_EQUIPMENTS', 1) }}
          </label>
          <select
            id="workout-equipment"
            @invalid="invalidateForm"
            :disabled="loading"
            v-model="defaultEquipmentId"
          >
            <option value=""></option>
            <option
              v-for="equipment in equipmentsForSelect"
              :value="equipment.id"
              :key="equipment.id"
            >
              {{ equipment.label }}
            </option>
          </select>
        </div>
      </div>
      <ErrorMessage :message="errorMessages" v-if="errorMessages" />
      <div class="form-buttons">
        <button class="confirm" type="submit" :disabled="loading">
          {{ $t('buttons.SUBMIT') }}
        </button>
        <button
          class="cancel"
          @click.prevent="() => $router.push(`/profile/sports/${sport?.id}`)"
          :disabled="loading"
        >
          {{ $t('buttons.CANCEL') }}
        </button>
      </div>
    </form>
  </div>
</template>

<script setup lang="ts">
  import { capitalize, computed, onMounted, ref, toRefs, watch } from 'vue'
  import type { ComputedRef } from 'vue'
  import { useI18n } from 'vue-i18n'
  import { useRoute } from 'vue-router'

  import userSportComponent from '@/components/User/UserSports/userSportComponent'
  import { EQUIPMENTS_STORE } from '@/store/constants'
  import type { IEquipment } from '@/types/equipments'
  import type { ISport, ITranslatedSport } from '@/types/sports'
  import type { IAuthUserProfile } from '@/types/user'
  import { useStore } from '@/use/useStore'
  import { getEquipments } from '@/utils/equipments'
  import { convertDistance } from '@/utils/units'

  interface Props {
    authUser: IAuthUserProfile
    translatedSports: ITranslatedSport[]
  }
  const props = defineProps<Props>()

  const { t } = useI18n()
  const store = useStore()
  const route = useRoute()

  const { authUser, translatedSports } = toRefs(props)
  const {
    defaultColor,
    defaultEquipmentId,
    errorMessages,
    loading,
    sportColors,
    sportPayload,
    updateIsActive,
    updateSport,
  } = userSportComponent()

  const sport: ComputedRef<ITranslatedSport | null> = computed(() =>
    getSport(translatedSports.value)
  )
  const equipments: ComputedRef<IEquipment[]> = computed(
    () => store.getters[EQUIPMENTS_STORE.GETTERS.EQUIPMENTS]
  )
  const equipmentsForSelect: ComputedRef<IEquipment[]> = computed(() =>
    equipments.value && sport.value
      ? getEquipments(
          equipments.value,
          t,
          'withIncludedIds',
          sport.value,
          sport.value.default_equipments.map((e) => e.id)
        )
      : []
  )
  const formErrors = ref(false)

  onMounted(() => {
    const labelInput = document.getElementById('sport-color')
    labelInput?.focus()
    if (!route.params.id) {
      return
    }
    if (route.params.id && sport.value?.id) {
      formatSportForm(sport.value, true)
    }
  })

  function getSport(sportsList: ITranslatedSport[]) {
    if (!route.params.id) {
      return null
    }
    const filteredSportList = sportsList.filter((sport) =>
      route.params.id ? sport.id === +route.params.id : null
    )
    if (filteredSportList.length === 0) {
      return null
    }
    return filteredSportList[0]
  }
  function formatSportForm(sport: ISport | null, withEquipments = false) {
    if (sport !== null) {
      sportPayload.sport_id = sport.id
      sportPayload.color = sport.color
        ? sport.color
        : sportColors
          ? sportColors[sport.label]
          : defaultColor
      sportPayload.is_active = sport.is_active_for_user
      sportPayload.stopped_speed_threshold = +`${
        authUser.value.imperial_units
          ? convertDistance(sport.stopped_speed_threshold, 'km', 'mi', 2)
          : parseFloat(sport.stopped_speed_threshold.toFixed(2))
      }`
      sportPayload.fromSport = true
      if (withEquipments) {
        defaultEquipmentId.value =
          sport.default_equipments.length > 0
            ? sport.default_equipments[0].id
            : ''
      }
    }
  }
  function updateSportPreferences() {
    sportPayload.default_equipment_ids = defaultEquipmentId.value
      ? [defaultEquipmentId.value]
      : []
    updateSport(authUser.value)
  }
  function invalidateForm() {
    formErrors.value = true
  }

  watch(
    () => sport.value,
    (sport) => {
      if (route.params.id && sport?.id) {
        formatSportForm(sport, true)
      }
    }
  )
</script>

<style scoped lang="scss">
  @import '~@/scss/vars.scss';

  #sport-edition {
    .form-items {
      display: flex;
      flex-direction: column;

      input[type='text'] {
        height: 20px;
      }
      .form-item {
        display: flex;
        flex-direction: column;
        padding: $default-padding 0;
      }
      .form-item-checkbox {
        display: flex;
        padding: $default-padding $default-padding $default-padding 0;
        gap: $default-padding * 0.5;
      }
      .sport-color {
        border: none;
        margin: 6px 1px 6px 0;
        padding: 0;
        width: 80px;
      }
    }

    .error-message {
      margin: $default-margin 0;
    }

    .form-buttons {
      display: flex;
      justify-content: flex-end;
      button {
        margin: $default-padding * 0.5;
      }
    }
  }
</style>
