export interface IEquipmentType {
  id: number
  is_active: boolean
  label: string
  has_equipments: boolean
}
export interface ITranslatedEquipmentType extends IEquipmentType {
  translatedLabel: string
}
export interface IEquipmentTypePayload {
  id: number
  isActive: boolean
}
