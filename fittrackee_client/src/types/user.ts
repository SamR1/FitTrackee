import { IRecord } from '@/types/workouts'

export interface IAuthUserProfile {
  admin: boolean
  bio: string | null
  birth_date: string | null
  created_at: string
  email: string
  first_name: string | null
  language: string | null
  last_name: string | null
  location: string | null
  nb_sports: number
  nb_workouts: number
  picture: string | boolean
  records: IRecord[]
  sports_list: number[]
  timezone: string
  total_distance: number
  total_duration: string
  username: string
  weekm: boolean
}

export interface ILoginRegisterFormData {
  username: string
  email: string
  password: string
  password_conf: string
}

export interface ILoginOrRegisterData {
  actionType: string
  formData: ILoginRegisterFormData
}
