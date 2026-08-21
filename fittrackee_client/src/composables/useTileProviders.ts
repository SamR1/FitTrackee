import { computed } from 'vue'
import type { ComputedRef } from 'vue'

import { TILE_PROVIDERS_STORE } from '@/store/constants'
import type {
  ITileProvider,
  ITileProviderForAdmin,
} from '@/types/tileProviders.ts'
import { useStore } from '@/use/useStore'

export default function useTileProviders() {
  const store = useStore()

  const tileProviders: ComputedRef<ITileProvider[] | ITileProviderForAdmin[]> =
    computed(() => store.getters[TILE_PROVIDERS_STORE.GETTERS.TILE_PROVIDERS])

  const availableTileProviders: ComputedRef<ITileProvider[]> = computed(() =>
    tileProviders.value.filter((provider) => provider.enabled)
  )
  const defaultTileProvider: ComputedRef<ITileProvider> = computed(
    () =>
      tileProviders.value.find((provider) => provider.default) as ITileProvider
  )

  const mapAttribution: ComputedRef<string> = computed(
    () => defaultTileProvider.value?.attribution || ''
  )

  function updateTileProvider(
    tileProviderId: string,
    enabled: boolean,
    defaultStatus: boolean
  ) {
    store.dispatch(TILE_PROVIDERS_STORE.ACTIONS.UPDATE_TILE_PROVIDER, {
      id: tileProviderId,
      default: defaultStatus,
      enabled,
    })
  }

  return {
    availableTileProviders,
    defaultTileProvider,
    mapAttribution,
    tileProviders,
    updateTileProvider,
  }
}
