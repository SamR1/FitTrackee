export interface IOAuth2Client {
  client_id: string
  client_description: string | null
  client_secret?: string
  id: number
  issued_at: string
  name: string
  redirect_uris: string[]
  scope: string
  website: string
}

export interface IOAuth2ClientPayload {
  client_name: string
  client_uri: string
  client_description: string | null
  redirect_uris: string[]
  scope: string
}

export interface IOauth2ClientsPayload {
  page?: number
}
