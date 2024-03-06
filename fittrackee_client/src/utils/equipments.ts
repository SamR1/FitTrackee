import type {
  IEquipment,
  IEquipmentType,
  ITranslatedEquipmentType,
} from '@/types/equipments'

const sortEquipmentTypes = (
  a: ITranslatedEquipmentType,
  b: ITranslatedEquipmentType
): number => {
  const equipmentTypeATranslatedLabel = a.translatedLabel.toLowerCase()
  const equipmentTypeBTranslatedLabel = b.translatedLabel.toLowerCase()
  return equipmentTypeATranslatedLabel > equipmentTypeBTranslatedLabel
    ? 1
    : equipmentTypeATranslatedLabel < equipmentTypeBTranslatedLabel
      ? -1
      : 0
}

export const translateEquipmentTypes = (
  equipmentTypes: IEquipmentType[],
  t: CallableFunction
): ITranslatedEquipmentType[] =>
  equipmentTypes
    .map((equipmentType) => ({
      ...equipmentType,
      translatedLabel: t(`equipment_types.${equipmentType.label}.LABEL`),
    }))
    .sort(sortEquipmentTypes)

const sortEquipments = (a: IEquipment, b: IEquipment): number => {
  const equipmentTypeALabel = a.label.toLowerCase()
  const equipmentTypeBLabel = b.label.toLowerCase()
  return equipmentTypeALabel > equipmentTypeBLabel
    ? 1
    : equipmentTypeALabel < equipmentTypeBLabel
      ? -1
      : 0
}

export const getEquipments = (
  equipments: IEquipment[],
  t: CallableFunction,
  activeStatus: 'all' | 'withIncludedIds' | 'is_active' = 'all',
  equipmentToIncludeIds: number[] = []
): IEquipment[] =>
  equipments
    .filter((equipment) =>
      activeStatus == 'all'
        ? true
        : activeStatus == 'withIncludedIds'
          ? equipmentToIncludeIds.includes(equipment.id) || equipment.is_active
          : equipment.is_active
    )
    .map((equipment) => {
      return {
        ...equipment,
        label: equipment.is_active
          ? equipment.label
          : `${equipment.label} (${t('common.INACTIVE')})`,
      }
    })
    .sort(sortEquipments)
