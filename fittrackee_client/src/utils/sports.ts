import { ISport } from '@/types/sports'
import { IWorkout } from '@/types/workouts'

export const sportColors: Record<string, string> = {
  'Cycling (Sport)': '#55A8A3',
  'Cycling (Transport)': '#98C3A9',
  Hiking: '#D0838A',
  'Mountain Biking': '#ECC77E',
  Running: '#926692',
  Walking: '#929292',
}

export const sportIdColors = (sports: ISport[]): Record<number, string> => {
  const colors: Record<number, string> = {}
  sports.map((sport) => (colors[sport.id] = sportColors[sport.label]))
  return colors
}

const sortSports = (a: ISport, b: ISport): number => {
  const sportALabel = a.label.toLowerCase()
  const sportBLabel = b.label.toLowerCase()
  return sportALabel > sportBLabel ? 1 : sportALabel < sportBLabel ? -1 : 0
}

export const translateSports = (
  sports: ISport[],
  t: CallableFunction,
  onlyActive = false
): ISport[] =>
  sports
    .filter((sport) => (onlyActive ? sport.is_active : true))
    .map((sport) => ({
      ...sport,
      label: t(`sports.${sport.label}.LABEL`),
    }))
    .sort(sortSports)

export const getSportImg = (workout: IWorkout, sports: ISport[]): string => {
  return sports
    .filter((sport) => sport.id === workout.sport_id)
    .map((sport) => sport.img)[0]
}
