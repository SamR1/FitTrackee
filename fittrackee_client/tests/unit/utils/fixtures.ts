import createI18n from '@/i18n'
import { ISport } from '@/types/sports'
import { translateSports } from '@/utils/sports'

const { t } = createI18n.global
export const sports: ISport[] = [
  {
    has_workouts: false,
    id: 1,
    img: '/img/sports/cycling-sport.png',
    is_active: true,
    label: 'Cycling (Sport)',
  },
  {
    has_workouts: false,
    id: 2,
    img: '/img/sports/cycling-transport.png',
    is_active: false,
    label: 'Cycling (Transport)',
  },
  {
    has_workouts: true,
    id: 3,
    img: '/img/sports/hiking.png',
    is_active: true,
    label: 'Hiking',
  },
]

export const translatedSports = translateSports(sports, t)
