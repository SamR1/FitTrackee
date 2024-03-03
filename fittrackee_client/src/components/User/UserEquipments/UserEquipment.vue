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
          :title="$t(`equipment_types.${equipment.equipment_type.label}.LABEL`)"
          :equipment-type-label="equipment.equipment_type.label"
        />
        <span>{{
          $t(`equipment_types.${equipment.equipment_type.label}.LABEL`)
        }}</span>
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
          :class="`fa fa-${equipment.is_active ? 'check-' : ''}square-o`"
          aria-hidden="true"
        />
      </dd>
    </dl>
    <div class="equipment-buttons">
      <button @click="$router.push(`/profile/equipments/${equipment.id}/edit`)">
        {{ $t('buttons.EDIT') }}
      </button>
      <button @click="$router.push('/profile/equipments')">
        {{ $t('buttons.BACK') }}
      </button>
    </div>
  </div>
  <div v-else>
    <p class="no-equipment">{{ $t('equipments.NO_EQUIPMENT') }}</p>
    <button @click="$router.push('/profile/equipments')">
      {{ $t('buttons.BACK') }}
    </button>
  </div>
</template>

<script setup lang="ts">
  import { capitalize, computed, toRefs } from 'vue'
  import type { ComputedRef } from 'vue'
  import { useRoute } from 'vue-router'

  import type { IEquipment } from '@/types/equipments'

  interface Props {
    equipments: IEquipment[]
  }
  const props = defineProps<Props>()

  const route = useRoute()

  const { equipments } = toRefs(props)
  const equipment: ComputedRef<IEquipment | null> = computed(() =>
    getEquipment(equipments.value)
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
  .equipment-buttons {
    display: flex;
    flex-wrap: wrap;
    gap: $default-padding;
  }
</style>
