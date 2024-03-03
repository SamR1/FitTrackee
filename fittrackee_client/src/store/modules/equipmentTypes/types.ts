import type {
  ActionContext,
  CommitOptions,
  DispatchOptions,
  Store as VuexStore,
} from 'vuex'

import { EQUIPMENT_TYPES_STORE } from '@/store/constants'
import type { IRootState } from '@/store/modules/root/types'
import type { IEquipmentType, IEquipmentTypePayload } from '@/types/equipments'

export interface IEquipmentTypesState {
  equipmentsTypes: IEquipmentType[]
}

export interface IEquipmentTypesActions {
  [EQUIPMENT_TYPES_STORE.ACTIONS.GET_EQUIPMENT_TYPES](
    context: ActionContext<IEquipmentTypesState, IRootState>
  ): void
  [EQUIPMENT_TYPES_STORE.ACTIONS.UPDATE_EQUIPMENT_TYPE](
    context: ActionContext<IEquipmentTypesState, IRootState>,
    payload: IEquipmentTypePayload
  ): void
}

export interface IEquipmentTypesGetters {
  [EQUIPMENT_TYPES_STORE.GETTERS.EQUIPMENT_TYPES](
    state: IEquipmentTypesState
  ): IEquipmentType[]
}

export type TEquipmentTypesMutations<S = IEquipmentTypesState> = {
  [EQUIPMENT_TYPES_STORE.MUTATIONS.SET_EQUIPMENT_TYPES](
    state: S,
    equipmentTypes: IEquipmentType[]
  ): void
}

export type TEquipmentTypesStoreModule<S = IEquipmentTypesState> = Omit<
  VuexStore<S>,
  'commit' | 'getters' | 'dispatch'
> & {
  dispatch<K extends keyof IEquipmentTypesActions>(
    key: K,
    payload?: Parameters<IEquipmentTypesActions[K]>[1],
    options?: DispatchOptions
  ): ReturnType<IEquipmentTypesActions[K]>
} & {
  getters: {
    [K in keyof IEquipmentTypesGetters]: ReturnType<IEquipmentTypesGetters[K]>
  }
} & {
  commit<
    K extends keyof TEquipmentTypesMutations,
    P extends Parameters<TEquipmentTypesMutations[K]>[1],
  >(
    key: K,
    payload?: P,
    options?: CommitOptions
  ): ReturnType<TEquipmentTypesMutations[K]>
}
