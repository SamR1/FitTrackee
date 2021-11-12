import createI18n from '@/i18n'
import { ISport } from '@/types/sports'
import { translateSports } from '@/utils/sports'

const { t } = createI18n.global
export const sports: ISport[] = [
  {
    color: null,
    has_workouts: false,
    id: 1,
    img: '/img/sports/cycling-sport.png',
    is_active: true,
    is_active_for_user: true,
    label: 'Cycling (Sport)',
    stopped_speed_threshold: 1,
  },
  {
    color: '#000000',
    has_workouts: false,
    id: 2,
    img: '/img/sports/cycling-transport.png',
    is_active: false,
    is_active_for_user: false,
    label: 'Cycling (Transport)',
    stopped_speed_threshold: 1,
  },
  {
    color: null,
    has_workouts: true,
    id: 3,
    img: '/img/sports/hiking.png',
    is_active: true,
    is_active_for_user: false,
    label: 'Hiking',
    stopped_speed_threshold: 0.1,
  },
]

export const translatedSports = translateSports(sports, t)
