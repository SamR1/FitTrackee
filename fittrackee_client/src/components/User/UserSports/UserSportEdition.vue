<template>
  <div id="sport-edition" v-if="sport">
    <Modal
      v-if="displayModal"
      :title="$t('common.CONFIRMATION')"
      :message="
        $t(
          `user.PROFILE.SPORT.CONFIRM_SPORT_RESET${sport.default_equipments ? '_WITH_EQUIPMENTS' : ''}`
        )
      "
      @confirmAction="resetSport()"
      @cancelAction="updateDisplayModal(false)"
      @keydown.esc="updateDisplayModal(false)"
    />
    <form @submit.prevent="updateSport">
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
            v-model="sportPayload.color"
            :disabled="loading"
          />
        </div>
        <div class="form-item">
          <label for="sport-threshold">
            {{ capitalize($t('equipments.EQUIPMENT_TYPE')) }}*
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
            {{ $t('user.PROFILE.SPORT.DEFAULT_EQUIPMENTS', 0) }}
          </label>
          <EquipmentsMultiSelect
            :equipments="equipmentsForMultiSelect"
            :workout-equipments="sportEquipments"
            name="sport-default-equipment"
            @updatedValues="updateEquipments"
            :disabled="loading"
          />
        </div>
      </div>
      <ErrorMessage :message="errorMessages" v-if="errorMessages" />
      <div class="form-buttons">
        <button
          :disabled="loading"
          class="warning"
          @click.prevent="updateDisplayModal(true)"
        >
          {{ $t('buttons.RESET') }}
        </button>
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
  import {
    capitalize,
    computed,
    inject,
    onMounted,
    reactive,
    ref,
    toRefs,
    watch,
  } from 'vue'
  import type { ComputedRef, Ref } from 'vue'
  import { useI18n } from 'vue-i18n'
  import { useRoute } from 'vue-router'

  import EquipmentsMultiSelect from '@/components/User/UserEquipments/EquipmentsMultiSelect.vue'
  import {
    AUTH_USER_STORE,
    EQUIPMENTS_STORE,
    ROOT_STORE,
  } from '@/store/constants'
  import type { IEquipment } from '@/types/equipments'
  import type { ISport, ITranslatedSport } from '@/types/sports'
  import type { IUserProfile, IUserSportPreferencesPayload } from '@/types/user'
  import { useStore } from '@/use/useStore'
  import { getEquipments } from '@/utils/equipments'

  interface Props {
    authUser: IUserProfile
    translatedSports: ITranslatedSport[]
  }
  const props = defineProps<Props>()

  const { t } = useI18n()
  const store = useStore()
  const route = useRoute()

  const { translatedSports } = toRefs(props)

  const defaultColor = '#838383'
  const sportColors = inject('sportColors') as Record<string, string>
  const sport: ComputedRef<ITranslatedSport | null> = computed(() =>
    getSport(translatedSports.value)
  )
  const equipments: ComputedRef<IEquipment[]> = computed(
    () => store.getters[EQUIPMENTS_STORE.GETTERS.EQUIPMENTS]
  )
  const equipmentsForMultiSelect: ComputedRef<IEquipment[]> = computed(() =>
    equipments.value
      ? getEquipments(
          equipments.value,
          t,
          'withIncludedIds',
          sport.value?.default_equipments.map((e) => e.id)
        )
      : []
  )
  const sportEquipments: ComputedRef<IEquipment[]> = computed(() =>
    sport.value?.default_equipments
      ? getEquipments(sport.value.default_equipments, t, 'all')
      : []
  )
  const errorMessages: ComputedRef<string | string[] | null> = computed(
    () => store.getters[ROOT_STORE.GETTERS.ERROR_MESSAGES]
  )
  const loading = computed(
    () => store.getters[AUTH_USER_STORE.GETTERS.USER_LOADING]
  )
  const displayModal: Ref<boolean> = ref(false)
  const sportPayload: IUserSportPreferencesPayload = reactive({
    sport_id: 0,
    color: null,
    is_active: true,
    stopped_speed_threshold: 1,
    default_equipment_ids: [],
    from_sport_id: null,
  })

  onMounted(() => {
    if (!route.params.id) {
      return
    }
    if (route.params.id && sport.value?.id) {
      formatForm(sport.value)
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
  function updateIsActive(event: Event) {
    sportPayload.is_active = (event.target as HTMLInputElement).checked
  }
  function updateEquipments(selectedIds: number[]) {
    sportPayload.default_equipment_ids = selectedIds
  }
  function formatForm(sport: ISport | null) {
    if (sport !== null) {
      sportPayload.sport_id = sport.id
      sportPayload.color = sport.color
        ? sport.color
        : sportColors
          ? sportColors[sport.label]
          : defaultColor
      sportPayload.is_active = sport.is_active_for_user
      sportPayload.stopped_speed_threshold = sport.stopped_speed_threshold
      sportPayload.from_sport_id = sport.id
      sportPayload.default_equipment_ids = sport.default_equipments.map(
        (e) => e.id
      )
    }
  }
  function updateSport(event: Event) {
    event.preventDefault()
    store.dispatch(
      AUTH_USER_STORE.ACTIONS.UPDATE_USER_SPORT_PREFERENCES,
      sportPayload
    )
  }
  function updateDisplayModal(value: boolean) {
    displayModal.value = value
  }
  function resetSport() {
    if (sportPayload.sport_id) {
      store.dispatch(AUTH_USER_STORE.ACTIONS.RESET_USER_SPORT_PREFERENCES, {
        sportId: sportPayload.sport_id,
        fromSport: true,
      })
    }
  }

  watch(
    () => sport.value,
    (sport) => {
      if (route.params.id && sport?.id) {
        formatForm(sport)
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
        padding: $default-padding;
      }
      .form-item-checkbox {
        display: flex;
        padding: $default-padding;
        gap: $default-padding * 0.5;
      }
      .sport-color {
        border: none;
        margin: 6px 1px 6px 0;
        padding: 0;
        width: 80px;
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
</style>
