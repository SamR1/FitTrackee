import { IRootState } from '@/store/modules/root/interfaces'
import { IApplication } from '@/types/application'

export const state: IRootState = {
  root: true,
  language: 'en',
  errorMessages: null,
  application: <IApplication>{},
  appLoading: false,
}
