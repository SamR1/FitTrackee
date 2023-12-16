import { enUS } from 'date-fns/locale'

import type { IRootState } from '@/store/modules/root/types'
import type { IApplication } from '@/types/application'

export const state: IRootState = {
  root: true,
  language: 'en',
  locale: enUS,
  errorMessages: null,
  application: <IApplication>{
    statistics: {
      sports: 0,
      uploads_dir_size: 0,
      users: 0,
      workouts: 0,
    },
  },
  appLoading: false,
  darkMode: null,
}
