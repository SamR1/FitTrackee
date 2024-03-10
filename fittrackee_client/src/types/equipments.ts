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

export interface IEquipment {
  creation_date: string
  description: string | null
  equipment_type: IEquipmentType
  id: number
  is_active: boolean
  label: string
  total_distance: number
  total_duration: number
  user_id: number
  workouts_count: number
}

export interface IAddEquipmentPayload {
  description: string | null
  equipmentTypeId: number
  label: string
}

export interface IPatchEquipmentPayload extends IAddEquipmentPayload {
  id: number
  isActive: boolean
}