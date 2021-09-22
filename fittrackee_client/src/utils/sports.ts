import { ISport } from '@/types/sports'

export const sportColors: Record<string, string> = {
  'Cycling (Sport)': '#55A8A3',
  'Cycling (Transport)': '#98C3A9',
  Hiking: '#D0838A',
  'Mountain Biking': '#ECC77E',
  Running: '#926692',
  Walking: '#929292',
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
