import { useStore as VuexStore } from 'vuex'

import { Store } from '@/store/types'

export function useStore(): Store {
  return VuexStore() as Store
}
