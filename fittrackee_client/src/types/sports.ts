export interface ISport {
  color: string | null
  has_workouts: boolean
  id: number
  img: string
  is_active: boolean
  is_active_for_user: boolean
  label: string
  stopped_speed_threshold: number
}

export interface ITranslatedSport extends ISport {
  translatedLabel: string
}

export interface ISportPayload {
  id: number
  isActive: boolean
}
