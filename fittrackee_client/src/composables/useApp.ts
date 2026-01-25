import type { Locale } from 'date-fns'
import { computed } from 'vue'
import type { ComputedRef } from 'vue'

import { ROOT_STORE } from '@/store/constants'
import type { IDisplayOptions, TAppConfig } from '@/types/application'
import type { IEquipmentError } from '@/types/equipments'
import type { TLanguage } from '@/types/locales'
import { useStore } from '@/use/useStore'

export default function useApp() {
  const store = useStore()

  const appLanguage: ComputedRef<TLanguage> = computed(
    () => store.getters[ROOT_STORE.GETTERS.LANGUAGE]
  )
  const appConfig: ComputedRef<TAppConfig> = computed(
    () => store.getters[ROOT_STORE.GETTERS.APP_CONFIG]
  )
  const appLoading: ComputedRef<boolean> = computed(
    () => store.getters[ROOT_STORE.GETTERS.APP_LOADING]
  )
  const displayOptions: ComputedRef<IDisplayOptions> = computed(
    () => store.getters[ROOT_STORE.GETTERS.DISPLAY_OPTIONS]
  )
  const darkMode: ComputedRef<boolean | null> = computed(
    () => store.getters[ROOT_STORE.GETTERS.DARK_MODE]
  )
  const darkTheme: ComputedRef<boolean> = computed(() => getDarkTheme())
  const elevationServices: ComputedRef<string[]> = computed(() => {
    const services = []
    if (appConfig.value.elevation_services.open_elevation) {
      services.push('Open Elevation')
    }
    if (appConfig.value.elevation_services.valhalla) {
      services.push('Valhalla')
    }
    return services
  })
  const elevationsProcessingItems: ComputedRef<string[]> = computed(() => {
    let items = ['file']
    if (elevationServices.value.includes('Open Elevation')) {
      items = items.concat(['open_elevation', 'open_elevation_smooth'])
    }
    if (elevationServices.value.includes('Valhalla')) {
      items.push('valhalla')
    }
    return items
  })

  const errorMessages: ComputedRef<string | string[] | IEquipmentError | null> =
    computed(() => store.getters[ROOT_STORE.GETTERS.ERROR_MESSAGES])
  const locale: ComputedRef<Locale> = computed(
    () => store.getters[ROOT_STORE.GETTERS.LOCALE]
  )

  function getDarkTheme() {
    if (
      darkMode.value === null &&
      window.matchMedia('(prefers-color-scheme: dark)').matches
    ) {
      return true
    }
    return darkMode.value === true
  }

  return {
    appConfig,
    appLanguage,
    appLoading,
    darkMode,
    darkTheme,
    displayOptions,
    elevationServices,
    elevationsProcessingItems,
    errorMessages,
    locale,
  }
}
