<template>
  <div id="user-equipment" class="description-list" v-if="equipment">
    <Modal
      v-if="displayModal"
      :title="$t('common.CONFIRMATION')"
      :message="$t('user.PROFILE.EQUIPMENTS.CONFIRM_EQUIPMENT_DELETION')"
      :strongMessage="equipment.label"
      @confirmAction="deleteEquipment"
      @cancelAction="updateDisplayModal(false)"
      @keydown.esc="updateDisplayModal(false)"
    />
    <dl>
      <dt>{{ capitalize($t('common.LABEL')) }}</dt>
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
        <span>
          {{ $t(`equipment_types.${equipment.equipment_type.label}.LABEL`) }}
        </span>
      </dd>
      <dt>{{ capitalize($t('workouts.WORKOUT', 0)) }}</dt>
      <dd>
        <router-link :to="`/workouts?equipment_id=${equipment.id}`">
          {{ equipment.workouts_count }}
        </router-link>
      </dd>
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
      <button class="danger" @click="displayModal = true">
        {{ $t('buttons.DELETE') }}
      </button>
      <button
        @click="
          $router.push(
            route.query.fromWorkoutId
              ? `/workouts/${route.query.fromWorkoutId}`
              : '/profile/equipments'
          )
        "
      >
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
  import { capitalize, computed, onUnmounted, ref, toRefs } from 'vue'
  import type { ComputedRef, Ref } from 'vue'
  import { useRoute } from 'vue-router'

  import { EQUIPMENTS_STORE, ROOT_STORE } from '@/store/constants'
  import type { IEquipment } from '@/types/equipments'
  import { useStore } from '@/use/useStore'

  interface Props {
    equipments: IEquipment[]
  }
  const props = defineProps<Props>()

  const store = useStore()
  const route = useRoute()

  const { equipments } = toRefs(props)
  const equipment: ComputedRef<IEquipment | null> = computed(() =>
    getEquipment(equipments.value)
  )
  const displayModal: Ref<boolean> = ref(false)

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
  function updateDisplayModal(display: boolean) {
    displayModal.value = display
  }
  function deleteEquipment() {
    if (equipment.value?.id) {
      store.dispatch(
        EQUIPMENTS_STORE.ACTIONS.DELETE_EQUIPMENT,
        equipment.value.id
      )
    }
  }

  onUnmounted(() => {
    store.commit(ROOT_STORE.MUTATIONS.EMPTY_ERROR_MESSAGES)
  })
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
