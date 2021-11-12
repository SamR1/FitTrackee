import { ISport, ITranslatedSport } from '@/types/sports'
import { IWorkout } from '@/types/workouts'

// TODO: allow user to change colors
export const sportColors: Record<string, string> = {
  'Cycling (Sport)': '#4c9792',
  'Cycling (Transport)': '#88af98',
  Hiking: '#bb757c',
  'Mountain Biking': '#d4b371',
  'Mountain Biking (Electric)': '#fc9d6f',
  Rowing: '#fcce72',
  Running: '#835b83',
  'Skiing (Alpine)': '#67a4bd',
  'Skiing (Cross Country)': '#9498d0',
  Trail: '#09a98a',
  Walking: '#838383',
}

export const sportIdColors = (sports: ISport[]): Record<number, string> => {
  const colors: Record<number, string> = {}
  sports.map((sport) => (colors[sport.id] = sportColors[sport.label]))
  return colors
}

const sortSports = (a: ITranslatedSport, b: ITranslatedSport): number => {
  const sportATranslatedLabel = a.translatedLabel.toLowerCase()
  const sportBTranslatedLabel = b.translatedLabel.toLowerCase()
  return sportATranslatedLabel > sportBTranslatedLabel
    ? 1
    : sportATranslatedLabel < sportBTranslatedLabel
    ? -1
    : 0
}

export const translateSports = (
  sports: ISport[],
  t: CallableFunction,
  onlyActive = false
): ITranslatedSport[] =>
  sports
    .filter((sport) => (onlyActive ? sport.is_active_for_user : true))
    .map((sport) => ({
      ...sport,
      translatedLabel: t(`sports.${sport.label}.LABEL`),
    }))
    .sort(sortSports)

export const getSportLabel = (workout: IWorkout, sports: ISport[]): string => {
  return sports
    .filter((sport) => sport.id === workout.sport_id)
    .map((sport) => sport.label)[0]
}

export const getSportColor = (
  workout: IWorkout,
  sports: ISport[]
): string | null => {
  return sports
    .filter((sport) => sport.id === workout.sport_id)
    .map((sport) => sport.color)[0]
}
