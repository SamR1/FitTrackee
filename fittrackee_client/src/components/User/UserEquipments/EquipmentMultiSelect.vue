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
    @remove="removeSelectedEquipmentItems()"
    @update:model-value="test"
  />
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

  function test(selectValues: IEquipment[]) {
    if (selectValues.length > 1) {
      // prevent selecting all group items (only one piece of equipment per
      // equipment type is allowed)
      selectedPieces.value = [...validSelectedPieces.value]
    }
  }
  function addSelectedEquipmentItems(selectValue: IEquipment | IEquipment[]) {
    // prevent selecting all group items (only one piece of equipment per
    // equipment type is allowed)
    if (!Array.isArray(selectValue)) {
      selectedPieces.value = [...validSelectedPieces.value, selectValue]
      selectedPieces.value = selectedPieces.value.filter(
        (e) =>
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
  function removeSelectedEquipmentItems() {
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
  @use '~@/scss/multiselect.scss' as *;
  ::v-deep(.multiselect__option) {
    padding-left: 20px;
  }
  ::v-deep(.multiselect__option--group) {
    padding-left: 10px;
    font-weight: bold;
    cursor: default;
  }
</style>
