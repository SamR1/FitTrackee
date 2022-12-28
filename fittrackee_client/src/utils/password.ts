import { zxcvbnOptions } from '@zxcvbn-ts/core'

export const loadLanguagePackage = async (language: string) => {
  // no package available for norwegian bokmal and dutch (Nederlands)
  // fallback to english
  switch (language) {
    case 'fr':
      return await import(
        /* webpackChunkName: "password.fr" */ '@zxcvbn-ts/language-fr'
      )
    case 'de':
      return await import(
        /* webpackChunkName: "password.de" */ '@zxcvbn-ts/language-de'
      )
    case 'it':
      return await import(
        /* webpackChunkName: "password.it" */ '@zxcvbn-ts/language-it'
      )
    default:
      return await import(
        /* webpackChunkName: "password.en" */ '@zxcvbn-ts/language-en'
      )
  }
}

export const setZxcvbnOptions = async (language: string) => {
  const zxcvbnCommonPackage = await import(
    /* webpackChunkName: "password" */ '@zxcvbn-ts/language-common'
  )
  const zxcvbnLanguagePackage = await loadLanguagePackage(language)
  const options = {
    graphs: zxcvbnCommonPackage.default.adjacencyGraphs,
    dictionary: {
      ...zxcvbnCommonPackage.default.dictionary,
      ...zxcvbnLanguagePackage.default.dictionary,
    },
  }
  zxcvbnOptions.setOptions(options)
}

export const getPasswordStrength = (strength: number): string => {
  switch (strength) {
    case 2:
      return 'AVERAGE'
    case 3:
      return 'GOOD'
    case 4:
      return 'STRONG'
    default:
      return 'WEAK'
  }
}
