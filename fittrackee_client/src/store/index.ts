import { createStore } from 'vuex'

import root from '@/store/modules/root'
import { IRootState } from '@/store/modules/root/interfaces'

const store = createStore<IRootState>(root)

export default store
