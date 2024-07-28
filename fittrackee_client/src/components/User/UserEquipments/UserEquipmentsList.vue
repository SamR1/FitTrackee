<template>
  <div id="user-equipments-list">
    <div class="mobile-display" v-if="equipments.length > 0">
      <button
        v-if="!isEdition"
        @click="$router.push('/profile/edit/equipments')"
      >
        {{ $t('equipments.EDIT_EQUIPMENTS') }}
      </button>
      <button
        v-if="!isEdition"
        @click="$router.push('/profile/equipments/new')"
      >
        {{ $t('equipments.NEW_EQUIPMENT') }}
      </button>
      <button v-if="isEdition" @click="$router.push('/profile/equipments')">
        {{ $t('buttons.BACK') }}
      </button>
      <button v-else @click="$router.push('/')">
        {{ $t('common.HOME') }}
      </button>
    </div>
    <h1 v-if="!isEdition" class="equipments-list">
      {{ $t('user.PROFILE.EQUIPMENTS.YOUR_EQUIPMENTS') }}
    </h1>
    <p
      class="no-equipments"
      :class="{ edition: isEdition }"
      v-if="equipments.length === 0"
    >
      {{ $t('equipments.NO_EQUIPMENTS') }}
    </p>
    <div v-else>
      <template
        v-for="equipmentType in translatedEquipmentTypes"
        :key="equipmentType.label"
      >
        <template v-if="equipmentByTypes[equipmentType.id]">
          <h2>
            <EquipmentTypeImage
              :title="equipmentType.translatedLabel"
              :equipment-type-label="equipmentType.label"
            />
            {{ equipmentType.translatedLabel }}
            {{ equipmentType.is_active ? '' : `(${$t('common.INACTIVE')})` }}
          </h2>
          <div class="responsive-table">
            <table>
              <thead>
                <tr>
                  <th class="text-left">
                    {{ $t('common.LABEL') }}
                  </th>
                  <th class="text-left">
                    {{ $t('workouts.WORKOUT', 0) }}
                  </th>
                  <th class="text-left">
                    {{ capitalize($t('workouts.TOTAL_DISTANCE')) }}
                  </th>
                  <th class="text-left">
                    {{ $t('common.ACTIVE') }}
                  </th>
                  <th v-if="isEdition">
                    {{ $t('common.ACTION') }}
                  </th>
                  <th />
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="equipment in equipmentByTypes[equipmentType.id].sort(
                    sortEquipments
                  )"
                  :key="equipment.label"
                >
                  <td class="equipment-label">
                    <span class="cell-heading">
                      {{ $t('common.LABEL') }}
                    </span>
                    <router-link
                      :to="{ name: 'Equipment', params: { id: equipment.id } }"
                    >
                      {{ equipment.label }}
                    </router-link>
                  </td>
                  <td class="column">
                    <span class="cell-heading">
                      {{ $t('workouts.WORKOUT', 0) }}
                    </span>
                    <router-link
                      :to="`/workouts?equipment_id=${equipment.id}`"
                      v-if="equipment.workouts_count"
                    >
                      {{ equipment.workouts_count }}
                    </router-link>
                    <template v-else>{{ equipment.workouts_count }}</template>
                  </td>
                  <td class="column">
                    <span class="cell-heading">
                      {{ $t('workouts.TOTAL_DISTANCE', 0) }}
                    </span>
                    <Distance
                      :distance="equipment.total_distance"
                      unitFrom="km"
                      :digits="2"
                      :displayUnit="false"
                      :useImperialUnits="authUser.imperial_units"
                    />
                    <span>
                      {{ authUser.imperial_units ? 'miles' : 'km' }}
                    </span>
                  </td>
                  <td class="active">
                    <span class="cell-heading">
                      {{ $t('common.ACTIVE') }}
                    </span>
                    <i
                      :class="`fa fa${equipment.is_active ? '-check' : ''}`"
                      aria-hidden="true"
                    />
                  </td>
                  <td v-if="isEdition" class="action-buttons">
                    <span class="cell-heading">
                      {{ $t('user.PROFILE.SPORT.ACTION') }}
                    </span>
                    <button
                      @click="
                        $router.push(
                          `/profile/edit/equipments/${equipment.id}${isEdition ? '?fromEdition=true' : ''}`
                        )
                      "
                    >
                      {{ $t('buttons.EDIT') }}
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </template>
      </template>
    </div>
    <div class="equipments-list-buttons">
      <button
        v-if="!isEdition && equipments.length > 0"
        @click="$router.push('/profile/edit/equipments')"
      >
        {{ $t('equipments.EDIT_EQUIPMENTS') }}
      </button>
      <button
        v-if="!isEdition"
        @click="$router.push('/profile/equipments/new')"
      >
        {{ $t('equipments.NEW_EQUIPMENT') }}
      </button>
      <button v-if="isEdition" @click="$router.push('/profile/equipments')">
        {{ $t('buttons.BACK') }}
      </button>
      <button v-else @click="$router.push('/')">{{ $t('common.HOME') }}</button>
    </div>
  </div>
</template>

<script setup lang="ts">
  import { capitalize, computed, toRefs } from 'vue'
  import type { ComputedRef } from 'vue'

  import type { IEquipment, ITranslatedEquipmentType } from '@/types/equipments'
  import type { IAuthUserProfile } from '@/types/user'
  import { sortEquipments } from '@/utils/equipments'

  interface Props {
    equipments: IEquipment[]
    translatedEquipmentTypes: ITranslatedEquipmentType[]
    authUser: IAuthUserProfile
    isEdition: boolean
  }
  const props = defineProps<Props>()
  const { authUser, isEdition, equipments, translatedEquipmentTypes } =
    toRefs(props)

  const equipmentByTypes: ComputedRef<Record<number, IEquipment[]>> = computed(
    () => formatEquipmentsList(equipments.value)
  )

  function formatEquipmentsList(equipments: IEquipment[]) {
    const equipmentByTypes: Record<number, IEquipment[]> = {}
    equipments.map((equipment) => {
      if (equipment.equipment_type.id in equipmentByTypes) {
        equipmentByTypes[equipment.equipment_type.id].push(equipment)
      } else {
        equipmentByTypes[equipment.equipment_type.id] = [equipment]
      }
    })
    return equipmentByTypes
  }
</script>

<style scoped lang="scss">
  @import '~@/scss/vars.scss';
  #user-equipments-list {
    padding: $default-padding 0;
    h1 {
      font-size: 1.05em;
      font-weight: bold;
    }
    h2 {
      font-size: 1em;
      font-weight: bold;

      display: flex;
      gap: $default-padding * 0.5;
      margin: $default-margin * 2 0 $default-margin * 0.5;

      .equipment-type-img {
        height: 25px;
        width: 25px;
        margin: 0;
      }
    }
    table {
      th {
        text-transform: lowercase;
      }
      td {
        &.equipment-label {
          width: 280px;
        }
        &.column {
          min-width: 80px;
        }
        &.active {
          width: 40px;
        }
      }
    }
    .mobile-display {
      display: none;
    }
    .no-equipments {
      font-style: italic;
    }
    .equipments-list-buttons {
      display: flex;
      gap: $default-padding;
      flex-wrap: wrap;
    }

    @media screen and (max-width: $small-limit) {
      table {
        td {
          &.column {
            min-width: initial;
          }
          &.equipment-label,
          &.active,
          &.action-buttons {
            width: 45%;
          }
        }
      }

      .edition-buttons {
        justify-content: center;
      }
      .mobile-display {
        display: flex;
        flex-wrap: wrap;
        gap: $default-margin;
        margin: $default-margin 0 $default-margin * 2;
      }
    }
    @media screen and (max-width: $x-small-limit) {
      table {
        td {
          &.equipment-label,
          &.active,
          &.action-buttons {
            width: 100%;
          }
        }
      }
    }
  }
</style>
