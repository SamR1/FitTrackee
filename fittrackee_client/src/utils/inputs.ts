import linkifyHtml from 'linkify-html'
import { marked } from 'marked'
import sanitizeHtml from 'sanitize-html'

export const linkifyAndClean = (input: string): string => {
  return sanitizeHtml(linkifyHtml(input, { target: '_blank' }), {
    allowedTags: ['a'],
    disallowedTagsMode: 'escape',
  })
}

export const convertToMarkdown = (input: string): string => {
  const markdown = marked.parse(input, { breaks: true })
  return sanitizeHtml(markdown as string)
}
