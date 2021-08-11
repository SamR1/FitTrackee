import { createStore } from 'vuex'

import { IRootState } from '@/store/modules/root/interfaces'
import root from '@/store/modules/root'

const store = createStore<IRootState>(root)

export default store
