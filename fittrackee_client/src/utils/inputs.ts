import linkifyHtml from 'linkify-html'
import sanitizeHtml from 'sanitize-html'

import { ICustomTextareaData, IUsernameSuggestion } from '@/types/forms'

export const linkifyAndClean = (input: string): string => {
  return sanitizeHtml(
    linkifyHtml(input, {
      target: '_blank',
      validate: {
        email: () => false,
      },
    }),
    {
      allowedTags: ['a', 'p', 'span'],
    }
  )
}

export const getUsernameQuery = (
  textareaData: ICustomTextareaData
): IUsernameSuggestion => {
  const { value, selectionStart } = textareaData
  const usernameStartPosition = value.slice(0, selectionStart).search(/@\S+$/)
  const usernameEndPosition = value.slice(selectionStart).search(/\s/)
  const usernameQuery =
    usernameStartPosition < 0
      ? ''
      : usernameEndPosition < 0
      ? value.slice(usernameStartPosition + 1)
      : value.slice(
          usernameStartPosition + 1,
          usernameEndPosition + selectionStart
        )
  return usernameQuery.trim().length > 1
    ? {
        position: usernameStartPosition,
        usernameQuery: usernameQuery,
      }
    : {
        position: null,
        usernameQuery: null,
      }
}

export const replaceUsername = (
  text: string,
  position: number,
  usernameQuery: string,
  username: string
): string => {
  return (
    text.substring(0, position + 1) +
    username +
    text.substring(position + 1 + usernameQuery.length)
  )
}
