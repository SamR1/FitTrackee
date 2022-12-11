import { createI18n, LocaleMessages, VueMessageType } from 'vue-i18n'

/**
 * Load locale messages
 *
 * The loaded `JSON` locale messages is pre-compiled by `@intlify/vue-i18n-loader`, which is integrated into `vue-cli-plugin-i18n`.
 * See: https://github.com/intlify/vue-i18n-loader#rocket-i18n-resource-pre-compilation
 */
const disabledLanguages = ['it', 'nb'] // to update after translations release

function loadLocaleMessages(): Record<string, LocaleMessages<VueMessageType>> {
  const locales = require.context('./locales', true, /[A-Za-z0-9-_,\s]+\.ts$/i)
  const messages: Record<string, LocaleMessages<VueMessageType>> = {}
  locales.keys().forEach((key) => {
    const matched = key.match(/([A-Za-z0-9-_]+)\./i)
    if (
      matched &&
      matched.length > 1 &&
      !disabledLanguages.includes(matched[1])
    ) {
      const locale = matched[1]
      messages[locale] = locales(key).default
    }
  })
  return messages
}

export default createI18n({
  legacy: false,
  locale: 'en',
  fallbackLocale: 'en',
  globalInjection: true,
  messages: loadLocaleMessages(),
})
