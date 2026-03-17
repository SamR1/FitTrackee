<template>
  <Multiselect
    v-if="sports"
    placeholder=""
    :id="name"
    :name="name"
    :disabled="disabled"
    v-model="selectedSports"
    :multiple="true"
    :options="sports"
    :taggable="true"
    label="translatedLabel"
    track-by="id"
    :selectLabel="$t('workouts.MULTISELECT.selectLabel')"
    :selectedLabel="$t('workouts.MULTISELECT.selectedLabel')"
    :deselectLabel="$t('workouts.MULTISELECT.deselectLabel')"
    @update:model-value="updateSelectedSports"
  />
</template>

<script setup lang="ts">
  import { onBeforeMount, ref, toRefs, watch } from 'vue'
  import type { Ref } from 'vue'
  import Multiselect from 'vue-multiselect'

  import type { ITranslatedSport } from '@/types/sports'

  interface Props {
    sports: ITranslatedSport[]
    name: string
    equipmentSports?: ITranslatedSport[]
    disabled?: boolean
  }
  const props = withDefaults(defineProps<Props>(), {
    equipmentSports: () => [],
    disabled: false,
  })
  const { equipmentSports, name, sports } = toRefs(props)

  const emit = defineEmits(['updatedValues'])

  const selectedSports: Ref<ITranslatedSport[]> = ref([])

  function updateSelectedSports(sportsList: ITranslatedSport[]) {
    emit(
      'updatedValues',
      sportsList.map((e) => e.id)
    )
  }

  watch(
    () => equipmentSports.value,
    async (newEquipmentSports: ITranslatedSport[]) => {
      selectedSports.value = newEquipmentSports
      updateSelectedSports(newEquipmentSports)
    }
  )

  onBeforeMount(() => {
    if (equipmentSports.value) {
      selectedSports.value = equipmentSports.value
    }
  })
</script>

<style scoped lang="scss">
  @use '~@/scss/multiselect.scss' as *;
</style>
