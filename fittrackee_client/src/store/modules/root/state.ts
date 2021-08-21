import { IRootState, IApplication } from '@/store/modules/root/interfaces'

export const state: IRootState = {
  root: true,
  language: 'en',
  errorMessages: null,
  application: <IApplication>{},
  appLoading: false,
}
