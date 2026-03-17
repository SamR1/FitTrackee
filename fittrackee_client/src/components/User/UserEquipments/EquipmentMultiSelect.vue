<template>
  <Multiselect
    v-if="equipmentList"
    placeholder=""
    :id="name"
    :name="name"
    :disabled="disabled"
    v-model="selectedPieces"
    :multiple="true"
    :options="equipmentList"
    :taggable="true"
    label="label"
    track-by="id"
    group-values="items"
    group-label="type"
    :group-select="true"
    :selectLabel="$t('workouts.MULTISELECT.selectLabel')"
    :selectedLabel="$t('workouts.MULTISELECT.selectedLabel')"
    :deselectLabel="$t('workouts.MULTISELECT.deselectLabel')"
    selectGroupLabel=""
    deselectGroupLabel=""
    @select="addSelectedEquipmentItems"
    @remove="removeSelectedEquipmentItems"
    @update:model-value="updateItems"
  >
    <template #tag="{ option, remove }">
      <span class="multiselect__tag">
        <span class="multiselect__tag_equipment">
          <EquipmentTypeImage
            :title="$t(`equipment_types.${option.equipment_type.label}.LABEL`)"
            :equipment-type-label="option.equipment_type.label"
          />
          <span>{{ option.label }}</span>
          <i
            tabindex="1"
            @keydown.enter.prevent="remove(option)"
            @mousedown.prevent="remove(option)"
            class="multiselect__tag-icon"
          />
        </span>
      </span>
    </template>
  </Multiselect>
</template>

<script setup lang="ts">
  import { onBeforeMount, ref, toRefs, watch } from 'vue'
  import type { Ref } from 'vue'
  import Multiselect from 'vue-multiselect'

  import type {
    IEquipment,
    IEquipmentMultiselectItemsGroup,
  } from '@/types/equipments.ts'

  interface Props {
    equipmentList: IEquipmentMultiselectItemsGroup[]
    name: string
    existingEquipmentList?: IEquipment[]
    disabled?: boolean
  }
  const props = withDefaults(defineProps<Props>(), {
    existingEquipmentList: () => [],
    disabled: false,
  })
  const { equipmentList, name, existingEquipmentList } = toRefs(props)

  const emit = defineEmits(['updatedValues'])

  const selectedPieces: Ref<IEquipment[]> = ref([])
  const validSelectedPieces: Ref<IEquipment[]> = ref([])

  function updateItems(selectValues: IEquipment[]) {
    if (selectValues.length > 1) {
      // prevent selecting all group items
      selectedPieces.value = [...validSelectedPieces.value]
    }
  }
  function addSelectedEquipmentItems(selectValue: IEquipment | IEquipment[]) {
    // prevent selecting all group items
    if (!Array.isArray(selectValue)) {
      selectedPieces.value = [...validSelectedPieces.value, selectValue]
      selectedPieces.value = selectedPieces.value.filter(
        (e) =>
          e.equipment_type.label === 'Misc' ||
          e.equipment_type.id !== selectValue.equipment_type.id ||
          e.id === selectValue.id
      )
    }
    validSelectedPieces.value = [...selectedPieces.value]
    emit(
      'updatedValues',
      selectedPieces.value.map((e) => e.id)
    )
  }
  function removeSelectedEquipmentItems(selectValue: IEquipment) {
    selectedPieces.value = selectedPieces.value.filter(
      (e) => e.id !== selectValue.id
    )
    validSelectedPieces.value = selectedPieces.value
    emit(
      'updatedValues',
      selectedPieces.value.map((e) => e.id)
    )
  }

  watch(
    () => existingEquipmentList.value,
    async (newEquipmentList: IEquipment[]) => {
      selectedPieces.value = newEquipmentList
      validSelectedPieces.value = newEquipmentList
      emit(
        'updatedValues',
        selectedPieces.value.map((e) => e.id)
      )
    }
  )

  onBeforeMount(() => {
    if (existingEquipmentList.value) {
      selectedPieces.value = existingEquipmentList.value
      validSelectedPieces.value = existingEquipmentList.value
    }
  })
</script>

<style scoped lang="scss">
  @use '~@/scss/vars.scss' as *;
  @use '~@/scss/multiselect.scss' as *;
  ::v-deep(.multiselect__option) {
    padding-left: $default-padding * 2;
  }
  ::v-deep(.multiselect__option--group) {
    padding-left: $default-padding;
    font-weight: bold;
    cursor: default;
  }
  .multiselect__tag {
    padding-left: $default-padding * 0.5;
    .multiselect__tag_equipment {
      display: flex;
      .equipment-type-img {
        height: 18px;
        width: 20px;
      }
    }
  }
</style>
