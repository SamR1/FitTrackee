import type { IOAuth2State } from '@/store/modules/oauth2/types'
import type { IPagination } from '@/types/api'
import type { IOAuth2Client } from '@/types/oauth'

export const oAuth2State: IOAuth2State = {
  client: <IOAuth2Client>{},
  clients: [],
  pagination: <IPagination>{},
  revocationSuccessful: false,
}
