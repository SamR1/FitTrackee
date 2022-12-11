import { zxcvbnOptions } from '@zxcvbn-ts/core'

export const setZxcvbnOptions = async (language: string) => {
  const zxcvbnCommonPackage = await import(
    /* webpackChunkName: "password" */ '@zxcvbn-ts/language-common'
  )
  const zxcvbnEnPackage = await import(
    /* webpackChunkName: "password" */ '@zxcvbn-ts/language-en'
  )
  const zxcvbnFrPackage = await import(
    /* webpackChunkName: "password" */ '@zxcvbn-ts/language-fr'
  )
  const zxcvbnDePackage = await import(
    /* webpackChunkName: "password" */ '@zxcvbn-ts/language-de'
  )
  const zxcvbnItPackage = await import(
    /* webpackChunkName: "password" */ '@zxcvbn-ts/language-it'
  )
  const zxcvbnLangPackages: Record<string, typeof zxcvbnEnPackage> = {
    de: zxcvbnDePackage,
    en: zxcvbnEnPackage,
    fr: zxcvbnFrPackage,
    it: zxcvbnItPackage,
    // no package available for norwegian bokmal, fallback on english
    nb: zxcvbnEnPackage,
    // no package available for dutch (Nederlands), fallback on english
    nl: zxcvbnEnPackage,
  }
  const zxcvbnPackage = zxcvbnLangPackages[language]
  const options = {
    graphs: zxcvbnCommonPackage.default.adjacencyGraphs,
    dictionary: {
      ...zxcvbnCommonPackage.default.dictionary,
      ...zxcvbnPackage.default.dictionary,
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
