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
  const zxcvbnLangPackages: Record<string, typeof zxcvbnEnPackage> = {
    en: zxcvbnEnPackage,
    fr: zxcvbnFrPackage,
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
