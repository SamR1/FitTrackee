import type {
  IEquipmentType,
  ITranslatedEquipmentType,
} from '@/types/equipments'

// TODO: refacto with sports?
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
