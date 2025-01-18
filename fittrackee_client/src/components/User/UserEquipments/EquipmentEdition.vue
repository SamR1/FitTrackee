<template>
  <div id="new-equipment">
    <h1 id="new-equipment-title" v-if="!equipmentForm.id">
      {{ $t('equipments.ADD_A_NEW_EQUIPMENT') }}
    </h1>
    <div id="equipment-form">
      <form :class="{ errors: formErrors }" @submit.prevent="submit">
        <div class="form-items">
          <div class="form-item">
            <label for="equipment-label">
              {{ capitalize($t('common.LABEL')) }}*
            </label>
            <input
              id="equipment-label"
              maxlength="50"
              type="text"
              required
              @invalid="invalidateForm"
              v-model="equipmentForm.label"
            />
            <div class="equipment-label-help">
              <span class="info-box">
                <i class="fa fa-info-circle" aria-hidden="true" />
                {{ $t('equipments.50_CHARACTERS_MAX') }}
              </span>
            </div>
          </div>
          <div class="form-item">
            <label for="equipment-type-id">
              {{ capitalize($t('equipments.EQUIPMENT_TYPE')) }}*
            </label>
            <select
              id="equipment-type-id"
              required
              @invalid="invalidateForm"
              v-model="equipmentForm.equipmentTypeId"
            >
              <option
                v-for="equipmentType in filteredEquipmentTypes"
                :value="equipmentType.id"
                :key="equipmentType.id"
              >
                {{ equipmentType.translatedLabel }}
                {{
                  equipmentType.is_active ? '' : `(${$t('common.INACTIVE')})`
                }}
              </option>
            </select>
          </div>
          <div
            class="equipment-warning"
            v-if="
              equipment?.workouts_count &&
              equipmentForm.equipmentTypeId !== equipment?.equipment_type.id
            "
          >
            <span class="info-box">
              <i
                class="fa fa-exclamation-triangle warning"
                aria-hidden="true"
              />
              {{ $t('equipments.ALL_WORKOUTS_ASSOCIATIONS_REMOVED') }}
            </span>
          </div>

          <div class="form-item">
            <label for="equipment-description">
              {{ $t('common.DESCRIPTION') }}
            </label>
            <CustomTextArea
              name="equipment-description"
              :charLimit="200"
              :input="equipmentForm.description"
              @updateValue="updateDescription"
            />
          </div>
          <div class="form-item-checkbox" v-if="equipmentForm.id">
            <label for="equipment-active">
              {{ capitalize($t('common.ACTIVE')) }}
            </label>
            <input
              id="equipment-active"
              name="equipment-active"
              type="checkbox"
              v-model="equipmentForm.isActive"
            />
          </div>
          <div class="form-item">
            <label for="equipment-sports">
              {{ capitalize($t('equipments.DEFAULT_FOR_SPORTS', 0)) }}
            </label>
            <SportsMultiSelect
              :sports="filteredSports"
              name="equipment-sports"
              :equipmentSports="equipmentTranslatedSports"
              :disabled="!equipmentForm.equipmentTypeId"
              @updatedValues="updateSports"
            />
          </div>
        </div>
        <ErrorMessage
          v-if="errorMessages"
          :message="errorMessages"
          :no-margin="true"
        />
        <div class="form-buttons">
          <button class="confirm" type="submit" :disabled="equipmentsLoading">
            {{ $t('buttons.SUBMIT') }}
          </button>
          <button
            class="cancel"
            :disabled="equipmentsLoading"
            @click.prevent="
              () =>
                $router.push(
                  equipment?.id
                    ? $route.query.fromEdition
                      ? '/profile/edit/equipments'
                      : `/profile/equipments/${equipment.id}`
                    : '/profile/equipments'
                )
            "
          >
            {{ $t('buttons.CANCEL') }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
  import {
    capitalize,
    computed,
    onMounted,
    reactive,
    ref,
    toRefs,
    watch,
  } from 'vue'
  import type { ComputedRef, Ref } from 'vue'
  import { useI18n } from 'vue-i18n'
  import { useRoute } from 'vue-router'

  import SportsMultiSelect from '@/components/User/UserEquipments/SportsMultiSelect.vue'
  import useApp from '@/composables/useApp'
  import useEquipments from '@/composables/useEquipments'
  import { EQUIPMENTS_STORE, SPORTS_STORE } from '@/store/constants'
  import type {
    IEquipment,
    IEquipmentType,
    ITranslatedEquipmentType,
  } from '@/types/equipments'
  import type { ITranslatedSport } from '@/types/sports'
  import { useStore } from '@/use/useStore'
  import { SPORT_EQUIPMENT_TYPES } from '@/utils/equipments'
  import { translateSports } from '@/utils/sports'

  interface Props {
    translatedEquipmentTypes: ITranslatedEquipmentType[]
    equipmentsLoading: boolean
  }
  const props = defineProps<Props>()
  const { equipmentsLoading, translatedEquipmentTypes } = toRefs(props)

  const store = useStore()
  const route = useRoute()
  const { t } = useI18n()

  const { errorMessages } = useApp()
  const { equipment } = useEquipments()

  const equipmentForm = reactive({
    id: '',
    label: '',
    description: '',
    equipmentTypeId: 0,
    isActive: true,
    defaultForSportIds: [] as number[],
  })
  const formErrors = ref(false)

  const translatedSports: ComputedRef<ITranslatedSport[]> = computed(() =>
    translateSports(store.getters[SPORTS_STORE.GETTERS.SPORTS], t)
  )
  const selectedEquipmentTypes: ComputedRef<IEquipmentType[]> = computed(() =>
    translatedEquipmentTypes.value.filter(
      (e) => e.id === equipmentForm.equipmentTypeId
    )
  )
  const filteredSports: ComputedRef<ITranslatedSport[]> = computed(() =>
    selectedEquipmentTypes.value.length > 0
      ? translatedSports.value.filter((s) =>
          SPORT_EQUIPMENT_TYPES[selectedEquipmentTypes.value[0].label].includes(
            s.label
          )
        )
      : []
  )
  const equipmentTranslatedSports: Ref<ITranslatedSport[]> = ref([])
  const filteredEquipmentTypes: ComputedRef<ITranslatedEquipmentType[]> =
    computed(() =>
      translatedEquipmentTypes.value.filter(
        (et) => et.is_active || equipment.value?.equipment_type.id === et.id
      )
    )

  function setEquipmentSports(equipment: IEquipment) {
    equipmentTranslatedSports.value = translateSports(
      translatedSports.value,
      t,
      'all'
    ).filter((s) => equipment.default_for_sport_ids.includes(s.id))
  }
  function formatForm(equipment: IEquipment) {
    equipmentForm.id = equipment.id
    equipmentForm.label = equipment.label
    equipmentForm.description = equipment.description
      ? equipment.description
      : ''
    equipmentForm.equipmentTypeId = equipment.equipment_type.id
    equipmentForm.isActive = equipment.is_active
    setEquipmentSports(equipment)
  }
  function submit() {
    store.dispatch(
      EQUIPMENTS_STORE.ACTIONS[
        equipmentForm.id ? 'UPDATE_EQUIPMENT' : 'ADD_EQUIPMENT'
      ],
      equipmentForm
    )
  }
  function updateDescription(value: string) {
    equipmentForm.description = value
  }
  function invalidateForm() {
    formErrors.value = true
  }
  function updateSports(selectedIds: number[]) {
    equipmentForm.defaultForSportIds = selectedIds
  }

  watch(
    () => equipment.value,
    (equipment) => {
      if (route.params.id && equipment?.id) {
        formatForm(equipment)
      }
    }
  )
  watch(
    () => equipmentForm.equipmentTypeId,
    (newEquipmentTypeId: number) => {
      if (
        equipment.value &&
        newEquipmentTypeId === equipment.value.equipment_type.id
      ) {
        setEquipmentSports(equipment.value)
      } else {
        equipmentTranslatedSports.value = []
      }
    }
  )

  onMounted(() => {
    const colorInput = document.getElementById('equipment-label')
    colorInput?.focus()
    if (!route.params.id) {
      return
    }
    if (route.params.id && equipment.value?.id) {
      formatForm(equipment.value)
    }
  })
</script>

<style scoped lang="scss">
  @import '~@/scss/vars.scss';

  #new-equipment {
    #new-equipment-title {
      font-size: 1.05em;
      font-weight: bold;
      padding: 0 $default-padding;
    }

    #equipment-form {
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
      }
      .equipment-label-help {
        margin-top: $default-margin * 1.5;
      }
      .equipment-warning {
        margin-top: $default-margin * 0.5;
        margin-bottom: $default-margin;
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
</style>
