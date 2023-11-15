import { useStore as VuexStore } from 'vuex'

import type { Store } from '@/store/types'

export function useStore(): Store {
  return VuexStore() as Store
}
