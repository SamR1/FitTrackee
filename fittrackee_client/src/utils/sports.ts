import type { ISport, ITranslatedSport, TActiveStatus } from '@/types/sports'
import type { IWorkout } from '@/types/workouts'

export const sportColors: Record<string, string> = {
  Canoeing: '#75b3be',
  'Cycling (Sport)': '#4c9792',
  'Cycling (Trekking)': '#a8af88',
  'Cycling (Transport)': '#88af98',
  'Cycling (Virtual)': '#64a360',
  Halfbike: '#d3638a',
  Hiking: '#bb757c',
  Kayaking: '#4978c4',
  'Mountain Biking': '#d4b371',
  'Mountain Biking (Electric)': '#fc9d6f',
  Mountaineering: '#48b3b7',
  'Open Water Swimming': '#4058a4',
  Paragliding: '#c23c50',
  Rowing: '#fcce72',
  Running: '#835b83',
  'Skiing (Alpine)': '#67a4bd',
  'Skiing (Cross Country)': '#9498d0',
  Snowshoes: '#5780a8',
  Swimrun: '#3d9fc9',
  Trail: '#09a98a',
  Walking: '#838383',
  Windsurfing: '#856ece',
}

export const sportIdColors = (sports: ISport[]): Record<number, string> => {
  const colors: Record<number, string> = {}
  sports.forEach(
    (sport) =>
      (colors[sport.id] = sport.color ? sport.color : sportColors[sport.label])
  )
  return colors
}

const sortSports = (a: ITranslatedSport, b: ITranslatedSport): number => {
  const sportATranslatedLabel = a.translatedLabel.toLowerCase()
  const sportBTranslatedLabel = b.translatedLabel.toLowerCase()
  if (sportATranslatedLabel > sportBTranslatedLabel) {
    return 1
  }
  return sportATranslatedLabel < sportBTranslatedLabel ? -1 : 0
}

export const translateSports = (
  sports: ISport[],
  t: CallableFunction,
  activeStatus: TActiveStatus = 'all',
  sportsToInclude: number[] = []
): ITranslatedSport[] =>
  sports
    .filter((sport) =>
      activeStatus === 'all'
        ? true
        : sportsToInclude.includes(sport.id) || sport[activeStatus]
    )
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
