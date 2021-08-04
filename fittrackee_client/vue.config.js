/* eslint-disable @typescript-eslint/no-var-requires */
const path = require('path')

module.exports = {
  configureWebpack: {
    performance: {
      maxEntrypointSize: 400000,
      maxAssetSize: 500000,
    },
  },
  chainWebpack: (config) => {
    config.plugin('html').tap((args) => {
      args[0].title = 'FitTrackee'
      return args
    })
  },
  publicPath: '/',
  outputDir: path.resolve(__dirname, '../fittrackee/dist/'),
  assetsDir: 'static',
  pluginOptions: {
    i18n: {
      locale: 'en',
      fallbackLocale: 'en',
      localeDir: 'locales',
      enableLegacy: false,
      runtimeOnly: false,
      compositionOnly: false,
      fullInstall: true,
    },
  },
}
