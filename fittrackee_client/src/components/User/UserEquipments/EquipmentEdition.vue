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
                v-for="equipmentType in translatedEquipmentTypes"
                :value="equipmentType.id"
                :key="equipmentType.id"
              >
                {{ equipmentType.translatedLabel }}
              </option>
            </select>
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
              type="checkbox"
              v-model="equipmentForm.isActive"
            />
          </div>
        </div>
        <ErrorMessage :message="errorMessages" v-if="errorMessages" />
        <div class="form-buttons">
          <button class="confirm" type="submit">
            {{ $t('buttons.SUBMIT') }}
          </button>
          <button
            class="cancel"
            @click.prevent="
              () =>
                $router.push(
                  equipment?.id
                    ? route.query.fromEdition
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
  import type { ComputedRef } from 'vue'
  import { useRoute } from 'vue-router'

  import { EQUIPMENTS_STORE, ROOT_STORE } from '@/store/constants'
  import type { IEquipment, ITranslatedEquipmentType } from '@/types/equipments'
  import { useStore } from '@/use/useStore'

  interface Props {
    equipments: IEquipment[]
    translatedEquipmentTypes: ITranslatedEquipmentType[]
  }
  const props = defineProps<Props>()

  const store = useStore()
  const route = useRoute()

  const { equipments, translatedEquipmentTypes } = toRefs(props)
  const equipment: ComputedRef<IEquipment | null> = computed(() =>
    getEquipment(equipments.value)
  )
  const errorMessages: ComputedRef<string | string[] | null> = computed(
    () => store.getters[ROOT_STORE.GETTERS.ERROR_MESSAGES]
  )
  const equipmentForm = reactive({
    id: 0,
    label: '',
    description: '',
    equipmentTypeId: 0,
    isActive: true,
  })
  const formErrors = ref(false)

  onMounted(() => {
    if (!route.params.id) {
      return
    }
    if (route.params.id && equipment.value?.id) {
      formatForm(equipment.value)
    }
  })

  function getEquipment(equipmentsList: IEquipment[]) {
    if (!route.params.id) {
      return null
    }
    const filteredEquipmentList = equipmentsList.filter((equipment) =>
      route.params.id ? equipment.id === +route.params.id : null
    )
    if (filteredEquipmentList.length === 0) {
      return null
    }
    return filteredEquipmentList[0]
  }
  function formatForm(equipment: IEquipment) {
    equipmentForm.id = equipment.id
    equipmentForm.label = equipment.label
    equipmentForm.description = equipment.description
      ? equipment.description
      : ''
    equipmentForm.equipmentTypeId = equipment.equipment_type.id
    equipmentForm.isActive = equipment.is_active
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

  watch(
    () => equipment.value,
    (equipment) => {
      if (route.params.id && equipment?.id) {
        formatForm(equipment)
      }
    }
  )
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
