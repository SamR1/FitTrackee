import { IOAuth2State } from '@/store/modules/oauth2/types'
import { IPagination } from '@/types/api'
import { IOAuth2Client } from '@/types/oauth'

export const oAuth2State: IOAuth2State = {
  client: <IOAuth2Client>{},
  clients: [],
  pagination: <IPagination>{},
}
