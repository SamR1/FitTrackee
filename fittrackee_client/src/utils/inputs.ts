import linkifyHtml from 'linkify-html'
import sanitizeHtml from 'sanitize-html'

export const linkifyAndClean = (input: string): string => {
  return sanitizeHtml(linkifyHtml(input, { target: '_blank' }), {
    allowedTags: ['a'],
    disallowedTagsMode: 'escape',
  })
}
