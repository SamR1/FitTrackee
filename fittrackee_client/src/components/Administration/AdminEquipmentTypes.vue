<template>
  <div id="admin-equipment-types" class="admin-card">
    <Card>
      <template #title>{{ $t('admin.EQUIPMENT_TYPES.TITLE') }}</template>
      <template #content>
        <button class="top-button" @click.prevent="$router.push('/admin')">
          {{ $t('admin.BACK_TO_ADMIN') }}
        </button>
        <div class="responsive-table">
          <table>
            <thead>
              <tr>
                <th>#</th>
                <th>{{ $t('admin.EQUIPMENT_TYPES.TABLE.IMAGE') }}</th>
                <th class="text-left">
                  {{ $t('admin.EQUIPMENT_TYPES.TABLE.LABEL') }}
                </th>
                <th>{{ $t('admin.EQUIPMENT_TYPES.TABLE.ACTIVE') }}</th>
                <th class="text-left equipment-type-action">
                  {{ $t('admin.ACTION') }}
                </th>
                <th />
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="equipmentType in translatedEquipmentTypes"
                :key="equipmentType.id"
              >
                <td class="text-center">
                  <span class="cell-heading">id</span>
                  {{ equipmentType.id }}
                </td>
                <td>
                  <span class="cell-heading">
                    {{ $t('admin.EQUIPMENT_TYPES.TABLE.IMAGE') }}
                  </span>
                  <EquipmentTypeImage
                    :title="equipmentType.translatedLabel"
                    :equipment-type-label="equipmentType.label"
                  />
                </td>
                <td class="equipment-type-label">
                  <span class="cell-heading">
                    {{ $t('admin.EQUIPMENT_TYPES.TABLE.LABEL') }}
                  </span>
                  {{ equipmentType.translatedLabel }}
                </td>
                <td class="text-center">
                  <span class="cell-heading">
                    {{ $t('admin.EQUIPMENT_TYPES.TABLE.ACTIVE') }}
                  </span>
                  <i
                    :class="`fa fa${equipmentType.is_active ? '-check' : ''}`"
                    aria-hidden="true"
                  />
                </td>
                <td class="equipment-type-action">
                  <span class="cell-heading">
                    {{ $t('admin.ACTION') }}
                  </span>
                  <div class="action-button">
                    <button
                      :class="{ danger: equipmentType.is_active }"
                      @click="
                        updateEquipmentTypeStatus(
                          equipmentType.id,
                          !equipmentType.is_active
                        )
                      "
                    >
                      {{
                        $t(
                          `buttons.${equipmentType.is_active ? 'DIS' : 'EN'}ABLE`
                        )
                      }}
                    </button>
                    <span
                      v-if="equipmentType.has_equipments"
                      class="has-equipments"
                    >
                      <i class="fa fa-warning" aria-hidden="true" />
                      {{ $t('admin.EQUIPMENT_TYPES.TABLE.HAS_EQUIPMENTS') }}
                    </span>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
          <ErrorMessage :message="errorMessages" v-if="errorMessages" />
          <button @click.prevent="$router.push('/admin')">
            {{ $t('admin.BACK_TO_ADMIN') }}
          </button>
        </div>
      </template>
    </Card>
  </div>
</template>

<script setup lang="ts">
  import { computed, onBeforeMount } from 'vue'
  import type { ComputedRef } from 'vue'
  import { useI18n } from 'vue-i18n'

  import { EQUIPMENTS_STORE, ROOT_STORE } from '@/store/constants'
  import type { ITranslatedEquipmentType } from '@/types/equipments'
  import { useStore } from '@/use/useStore'
  import { translateEquipmentTypes } from '@/utils/equipments'

  const { t } = useI18n()
  const store = useStore()

  const translatedEquipmentTypes: ComputedRef<ITranslatedEquipmentType[]> =
    computed(() =>
      translateEquipmentTypes(
        store.getters[EQUIPMENTS_STORE.GETTERS.EQUIPMENT_TYPES],
        t
      )
    )
  const errorMessages: ComputedRef<string | string[] | null> = computed(
    () => store.getters[ROOT_STORE.GETTERS.ERROR_MESSAGES]
  )

  onBeforeMount(() => loadEquipmentTypes())

  function loadEquipmentTypes() {
    store.dispatch(EQUIPMENTS_STORE.ACTIONS.GET_EQUIPMENT_TYPES)
  }
  function updateEquipmentTypeStatus(id: number, isActive: boolean) {
    store.dispatch(EQUIPMENTS_STORE.ACTIONS.UPDATE_EQUIPMENT_TYPE, {
      id,
      isActive,
    })
  }
</script>

<style lang="scss" scoped>
  @import '~@/scss/vars.scss';
  #admin-equipment-types {
    table {
      td {
        font-size: 1.1em;
      }
    }
    .equipment-type-img {
      height: 35px;
      width: 35px;
      margin: 0 auto;
    }
    .has-equipments {
      font-size: 0.95em;
      font-style: italic;
      padding: 0 $default-padding;
    }
    .equipment-type-action {
      padding-left: $default-padding * 4;
    }
    .action-button {
      display: block;
    }
    .top-button {
      display: none;
    }

    @media screen and (max-width: $small-limit) {
      .equipment-type-action {
        padding-left: $default-padding;
      }
      .has-equipments {
        padding-top: $default-padding * 0.5;
      }
      .action-button {
        display: flex;
        align-items: center;
        flex-wrap: wrap;
        flex-direction: column;
      }
      .top-button {
        display: block;
        margin-bottom: $default-margin * 2;
      }
    }
  }
</style>
