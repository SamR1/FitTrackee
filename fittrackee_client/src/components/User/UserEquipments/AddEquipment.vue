<template>
  <div id="new-equipment">
    <h1 id="new-equipment-title">{{ $t('equipments.ADD_A_NEW_EQUIPMENT') }}</h1>
    <div id="equipment-form">
      <form @submit.prevent="createEquipment">
        <div class="form-items">
          <div class="form-item">
            <label for="equipment-label">{{ $t('common.LABEL') }}*</label>
            <input
              id="equipment-label"
              type="text"
              required
              v-model="equipmentForm.label"
            />
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
          <div class="form-item">
            <label for="equipment-type-id">
              {{ capitalize($t('equipments.EQUIPMENT_TYPE')) }}*
            </label>
            <select
              id="equipment-type-id"
              required
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
        </div>
        <div class="form-buttons">
          <button class="confirm" type="submit">
            {{ $t('buttons.SUBMIT') }}
          </button>
          <button
            class="cancel"
            @click.prevent="() => $router.push('/profile/equipments')"
          >
            {{ $t('buttons.CANCEL') }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
  import { capitalize, reactive, toRefs } from 'vue'

  import { EQUIPMENTS_STORE } from '@/store/constants'
  import type { ITranslatedEquipmentType } from '@/types/equipments'
  import { useStore } from '@/use/useStore'

  interface Props {
    translatedEquipmentTypes: ITranslatedEquipmentType[]
  }
  const props = defineProps<Props>()

  const store = useStore()

  const { translatedEquipmentTypes } = toRefs(props)
  const equipmentForm = reactive({
    label: '',
    description: '',
    equipmentTypeId: 0,
  })

  function createEquipment() {
    store.dispatch(EQUIPMENTS_STORE.ACTIONS.ADD_EQUIPMENT, equipmentForm)
  }
  function updateDescription(value: string) {
    equipmentForm.description = value
  }
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
        .form-item-scope {
          padding: $default-padding;

          .form-item-scope-label {
            font-weight: bold;
          }

          .form-item-scope-checkboxes {
            padding-bottom: $default-padding;

            .scope-label {
              height: inherit;
            }
            .scope-description {
              font-style: italic;
              margin: 0 $default-margin * 0.5;
            }
          }
        }

        .form-item {
          display: flex;
          flex-direction: column;
          padding: $default-padding;
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
