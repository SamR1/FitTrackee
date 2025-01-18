export interface IDropdownOption {
  value: string
  label: string
}

export type TDropdownOptions = IDropdownOption[]

export interface ICustomTextareaData {
  value: string
  selectionStart: number
}

export interface IUsernameSuggestion {
  position: number | null
  usernameQuery: string | null
}
