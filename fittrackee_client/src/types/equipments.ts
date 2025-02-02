import type { TVisibilityLevels } from '@/types/user.ts'

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

export interface ILightEquipment {
  equipment_type: IEquipmentType
  is_active: boolean
  label: string
}

export interface IEquipment extends ILightEquipment {
  creation_date: string
  default_for_sport_ids: number[]
  description: string | null
  id: string
  total_distance: number
  total_duration: string
  total_moving: string
  user_id: number
  visibility: TVisibilityLevels
  workouts_count: number
}

export interface IAddEquipmentPayload {
  defaultForSportIds: number[]
  description: string | null
  equipmentTypeId: number
  label: string
  visibility: TVisibilityLevels
}

export interface IPatchEquipmentPayload extends IAddEquipmentPayload {
  id: string
  isActive: boolean
}

export interface IDeleteEquipmentPayload {
  id: string
  force?: true
}

export interface IEquipmentError {
  equipmentId: string
  equipmentLabel: string | null
  status: string
}
