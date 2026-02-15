import type {
  IEquipment,
  IEquipmentMultiselectItemsGroup,
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
  Shoes: [
    'Hiking',
    'Mountaineering',
    'Padel (Outdoor)',
    'Running',
    'Swimrun',
    'Tennis (Outdoor)',
    'Trail',
    'Walking',
    'Cycling (Sport)',
    'Cycling (Transport)',
    'Cycling (Trekking)',
    'Halfbike',
    'Mountain Biking',
    'Mountain Biking (Electric)',
  ],
  Bike: [
    'Cycling (Sport)',
    'Cycling (Transport)',
    'Cycling (Trekking)',
    'Halfbike',
    'Mountain Biking',
    'Mountain Biking (Electric)',
  ],
  'Bike Trainer': ['Cycling (Virtual)'],
  Board: ['Standup Paddleboarding', 'Windsurfing'],
  Kayak_Boat: [
    'Canoeing',
    'Canoeing (Whitewater)',
    'Kayaking',
    'Kayaking (Whitewater)',
    'Rowing',
  ],
  Skis: ['Skiing (Alpine)', 'Skiing (Cross Country)'],
  Snowshoes: ['Snowshoes'],
}

function groupByEquipmentType(list: IEquipment[]) {
  const map = new Map<string, IEquipment[]>()
  list.forEach((item) => {
    const key = item.equipment_type.label
    const collection = map.get(key)
    if (collection) {
      collection.push(item)
    } else {
      map.set(key, [item])
    }
  })
  return map
}

export const getEquipments = (
  equipments: IEquipment[],
  t: CallableFunction,
  activeStatus: 'all' | 'withIncludedIds' | 'is_active' = 'all',
  sport: ITranslatedSport | null = null,
  equipmentToIncludeIds: string[] = []
) => {
  const equipmentMultiSelectList: IEquipmentMultiselectItemsGroup[] = []
  if (!sport) {
    return equipmentMultiSelectList
  }

  const validEquipmentPieces = equipments
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

  const equipmentList = groupByEquipmentType(validEquipmentPieces)
  // eslint-disable-next-line @typescript-eslint/ban-ts-comment
  // @ts-ignore
  for (const [key, value] of equipmentList) {
    equipmentMultiSelectList.push({
      type: t(`equipment_types.${key}.LABEL`),
      items: value.sort(sortEquipments),
    })
  }
  return equipmentMultiSelectList
}
