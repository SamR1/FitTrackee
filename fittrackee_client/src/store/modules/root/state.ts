import { enUS } from 'date-fns/locale'

import { IRootState } from '@/store/modules/root/types'
import { IApplication } from '@/types/application'

export const state: IRootState = {
  root: true,
  language: 'en',
  locale: enUS,
  errorMessages: null,
  application: <IApplication>{},
  appLoading: false,
}
