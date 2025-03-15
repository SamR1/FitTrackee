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
  if (equipmentTypeATranslatedLabel > equipmentTypeBTranslatedLabel) {
    return 1
  }
  return equipmentTypeATranslatedLabel < equipmentTypeBTranslatedLabel ? -1 : 0
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
  const equipmentALabel = a.label.toLowerCase()
  const equipmentBLabel = b.label.toLowerCase()
  if (equipmentALabel > equipmentBLabel) {
    return 1
  }
  return equipmentALabel < equipmentBLabel ? -1 : 0
}

export const SPORT_EQUIPMENT_TYPES: Record<string, string[]> = {
  Shoes: ['Hiking', 'Mountaineering', 'Running', 'Swimrun', 'Trail', 'Walking'],
  Bike: [
    'Cycling (Sport)',
    'Cycling (Transport)',
    'Cycling (Trekking)',
    'Mountain Biking',
    'Mountain Biking (Electric)',
  ],
  'Bike Trainer': ['Cycling (Virtual)'],
  Kayak_Boat: ['Canoeing', 'Rowing', 'Kayaking'],
  Skis: ['Skiing (Alpine)', 'Skiing (Cross Country)'],
  Snowshoes: ['Snowshoes'],
}

export const getEquipments = (
  equipments: IEquipment[],
  t: CallableFunction,
  activeStatus: 'all' | 'withIncludedIds' | 'is_active' = 'all',
  sport: ITranslatedSport | null = null,
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
