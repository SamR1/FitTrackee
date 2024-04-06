import type {
  IEquipment,
  IEquipmentType,
  ITranslatedEquipmentType,
} from '@/types/equipments'
import type { ITranslatedSport } from '@/types/sports'

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

export const sortEquipments = (a: IEquipment, b: IEquipment): number => {
  const equipmentTypeALabel = a.label.toLowerCase()
  const equipmentTypeBLabel = b.label.toLowerCase()
  return equipmentTypeALabel > equipmentTypeBLabel
    ? 1
    : equipmentTypeALabel < equipmentTypeBLabel
      ? -1
      : 0
}

export const SPORT_EQUIPMENT_TYPES: Record<string, string[]> = {
  Shoes: ['Hiking', 'Mountaineering', 'Running', 'Trail', 'Walking'],
  Bike: [
    'Cycling (Sport)',
    'Cycling (Transport)',
    'Cycling (Trekking)',
    'Mountain Biking',
    'Mountain Biking (Electric)',
  ],
  'Bike Trainer': ['Cycling (Virtual)'],
  Kayak_Boat: ['Rowing'],
  Skis: ['Skiing (Alpine)', 'Skiing (Cross Country)'],
  Snowshoes: ['Snowshoes'],
}

export const getEquipments = (
  equipments: IEquipment[],
  t: CallableFunction,
  activeStatus: 'all' | 'withIncludedIds' | 'is_active' = 'all',
  sport: ITranslatedSport | null,
  equipmentToIncludeIds: string[] = []
): IEquipment[] => {
  if (!sport) {
    return []
  }
  return equipments
    .filter((equipment) =>
      SPORT_EQUIPMENT_TYPES[equipment.equipment_type.label].includes(
        sport.label
      )
    )
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
}
