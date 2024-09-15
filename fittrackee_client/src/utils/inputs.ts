import linkifyHtml from 'linkify-html'
import sanitizeHtml from 'sanitize-html'

export const cleanInput = (input: string): string => {
  return sanitizeHtml(input, {
    allowedTags: ['a'],
    disallowedTagsMode: 'escape',
  })
}

export const linkifyAndClean = (input: string): string => {
  return cleanInput(linkifyHtml(input, { target: '_blank' }))
}
