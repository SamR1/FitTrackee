export interface ISport {
  has_workouts: boolean
  id: number
  img: string
  is_active: boolean
  label: string
}
export interface ITranslatedSport extends ISport {
  translatedLabel: string
}
