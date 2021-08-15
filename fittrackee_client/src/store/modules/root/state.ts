import { IRootState } from '@/store/modules/root/interfaces'
import { IApplication } from '@/store/modules/root/interfaces'

export const state: IRootState = {
  root: true,
  language: 'en',
  errorMessages: null,
  application: <IApplication>{},
}
