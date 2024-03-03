import type {
  ActionContext,
  CommitOptions,
  DispatchOptions,
  Store as VuexStore,
} from 'vuex'

import { EQUIPMENTS_STORE } from '@/store/constants'
import type { IRootState } from '@/store/modules/root/types'
import type {
  IAddEquipmentPayload,
  IEquipment,
  IEquipmentType,
  IEquipmentTypePayload,
  IPatchEquipmentPayload,
} from '@/types/equipments'

export interface IEquipmentTypesState {
  equipmentTypes: IEquipmentType[]
  equipments: IEquipment[]
}

export interface IEquipmentsActions {
  [EQUIPMENTS_STORE.ACTIONS.ADD_EQUIPMENT](
    context: ActionContext<IEquipmentTypesState, IRootState>,
    payload: IAddEquipmentPayload
  ): void
  [EQUIPMENTS_STORE.ACTIONS.DELETE_EQUIPMENT](
    context: ActionContext<IEquipmentTypesState, IRootState>,
    equipmentId: number
  ): void
  [EQUIPMENTS_STORE.ACTIONS.GET_EQUIPMENT](
    context: ActionContext<IEquipmentTypesState, IRootState>,
    equipmentId: number
  ): void
  [EQUIPMENTS_STORE.ACTIONS.GET_EQUIPMENTS](
    context: ActionContext<IEquipmentTypesState, IRootState>
  ): void
  [EQUIPMENTS_STORE.ACTIONS.GET_EQUIPMENT_TYPES](
    context: ActionContext<IEquipmentTypesState, IRootState>
  ): void
  [EQUIPMENTS_STORE.ACTIONS.UPDATE_EQUIPMENT](
    context: ActionContext<IEquipmentTypesState, IRootState>,
    payload: IPatchEquipmentPayload
  ): void
  [EQUIPMENTS_STORE.ACTIONS.UPDATE_EQUIPMENT_TYPE](
    context: ActionContext<IEquipmentTypesState, IRootState>,
    payload: IEquipmentTypePayload
  ): void
}

export interface IEquipmentsGetters {
  [EQUIPMENTS_STORE.GETTERS.EQUIPMENT](
    state: IEquipmentTypesState,
    equipmentId: number
  ): IEquipment
  [EQUIPMENTS_STORE.GETTERS.EQUIPMENTS](
    state: IEquipmentTypesState
  ): IEquipment[]
  [EQUIPMENTS_STORE.GETTERS.EQUIPMENT_TYPES](
    state: IEquipmentTypesState
  ): IEquipmentType[]
}

export type TEquipmentsMutations<S = IEquipmentTypesState> = {
  [EQUIPMENTS_STORE.MUTATIONS.REMOVE_EQUIPMENT](
    state: S,
    equipmentId: number
  ): void
  [EQUIPMENTS_STORE.MUTATIONS.SET_EQUIPMENT](
    state: S,
    equipment: IEquipment
  ): void
  [EQUIPMENTS_STORE.MUTATIONS.SET_EQUIPMENTS](
    state: S,
    equipments: IEquipment[]
  ): void
  [EQUIPMENTS_STORE.MUTATIONS.SET_EQUIPMENT_TYPES](
    state: S,
    equipmentTypes: IEquipmentType[]
  ): void
}

export type TEquipmentTypesStoreModule<S = IEquipmentTypesState> = Omit<
  VuexStore<S>,
  'commit' | 'getters' | 'dispatch'
> & {
  dispatch<K extends keyof IEquipmentsActions>(
    key: K,
    payload?: Parameters<IEquipmentsActions[K]>[1],
    options?: DispatchOptions
  ): ReturnType<IEquipmentsActions[K]>
} & {
  getters: {
    [K in keyof IEquipmentsGetters]: ReturnType<IEquipmentsGetters[K]>
  }
} & {
  commit<
    K extends keyof TEquipmentsMutations,
    P extends Parameters<TEquipmentsMutations[K]>[1],
  >(
    key: K,
    payload?: P,
    options?: CommitOptions
  ): ReturnType<TEquipmentsMutations[K]>
}
