<template>
  <div id="user-equipment" class="description-list" v-if="equipment">
    <dl>
      <dt>{{ $t('common.LABEL') }}</dt>
      <dd>{{ equipment.label }}</dd>
      <dt>{{ $t('common.DESCRIPTION') }}</dt>
      <dd>
        <span v-if="equipment.description">{{ equipment.description }}</span>
        <span v-else class="no-description">
          {{ $t('common.NO_DESCRIPTION') }}
        </span>
      </dd>
      <dt>{{ capitalize($t('equipments.EQUIPMENT_TYPE')) }}</dt>
      <dd class="equipment-type">
        <EquipmentTypeImage
          v-if="equipmentType"
          :title="equipmentType.translatedLabel"
          :equipment-type-label="equipmentType.label"
        />
        <span>{{ equipmentType?.translatedLabel }}</span>
      </dd>
      <dt>{{ capitalize($t('workouts.WORKOUT', 0)) }}</dt>
      <dd>{{ equipment.workouts_count }}</dd>
      <dt>{{ capitalize($t('workouts.DISTANCE', 0)) }}</dt>
      <dd>{{ equipment.total_distance }}</dd>
      <dt>{{ capitalize($t('workouts.DURATION', 0)) }}</dt>
      <dd>{{ equipment.total_duration }}</dd>
      <dt>{{ capitalize($t('common.ACTIVE', 0)) }}</dt>
      <dd>
        <i
          :class="`fa fa${equipment.is_active ? '-check' : ''}`"
          aria-hidden="true"
        />
      </dd>
    </dl>
  </div>
  <div v-else>
    <p class="no-equipment">{{ $t('equipments.NO_EQUIPMENT') }}</p>
  </div>
  <button @click="$router.push('/profile/equipments')">
    {{ $t('buttons.BACK') }}
  </button>
</template>

<script setup lang="ts">
  import { capitalize, computed, toRefs } from 'vue'
  import type { ComputedRef } from 'vue'
  import { useRoute } from 'vue-router'

  import type { IEquipment, ITranslatedEquipmentType } from '@/types/equipments'

  interface Props {
    equipments: IEquipment[]
    translatedEquipmentTypes: ITranslatedEquipmentType[]
  }
  const props = defineProps<Props>()

  const route = useRoute()

  const { equipments, translatedEquipmentTypes } = toRefs(props)
  const equipment: ComputedRef<IEquipment | null> = computed(() =>
    getEquipment(equipments.value)
  )
  const equipmentType: ComputedRef<ITranslatedEquipmentType | null> = computed(
    () => getEquipmentType(translatedEquipmentTypes.value)
  )

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

  function getEquipmentType(equipmentTypesList: ITranslatedEquipmentType[]) {
    if (!equipment.value?.id) {
      return null
    }
    const filteredEquipmentTypeList = equipmentTypesList.filter(
      (et) => et.id === equipment.value?.id
    )
    if (filteredEquipmentTypeList.length === 0) {
      return null
    }
    return filteredEquipmentTypeList[0]
  }
</script>

<style scoped lang="scss">
  @import '~@/scss/vars.scss';

  #user-equipment {
    .no-equipment {
      font-style: italic;
      padding: $default-padding 0;
    }
    .no-description {
      font-style: italic;
    }
    .equipment-type {
      display: flex;
      .equipment-type-img {
        height: 25px;
        width: 25px;
        margin: 0;
      }
    }
  }
</style>
