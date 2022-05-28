import { IOAuth2State } from '@/store/modules/oauth2/types'
import { IPagination } from '@/types/api'

export const oAuth2State: IOAuth2State = {
  clients: [],
  pagination: <IPagination>{},
}
