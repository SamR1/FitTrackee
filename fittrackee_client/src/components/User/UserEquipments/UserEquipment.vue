<template>
  <div id="user-equipment" class="description-list" v-if="equipment">
    <Modal
      v-if="displayModal"
      :title="$t('common.CONFIRMATION')"
      message="user.PROFILE.EQUIPMENTS.CONFIRM_EQUIPMENT_DELETION"
      :strongMessage="equipment.label"
      :warning="
        equipment.workouts_count > 0
          ? $t('user.PROFILE.EQUIPMENTS.EQUIPMENT_ASSOCIATED_WITH_WORKOUTS')
          : ''
      "
      @confirmAction="deleteEquipment"
      @cancelAction="updateDisplayModal(false)"
      @keydown.esc="updateDisplayModal(false)"
    />
    <dl>
      <dt>{{ capitalize($t('common.LABEL')) }}</dt>
      <dd>{{ equipment.label }}</dd>
      <dt>{{ capitalize($t('equipments.EQUIPMENT_TYPE')) }}</dt>
      <dd class="equipment-type">
        <EquipmentTypeImage
          :title="$t(`equipment_types.${equipment.equipment_type.label}.LABEL`)"
          :equipment-type-label="equipment.equipment_type.label"
        />
        <span>
          {{ $t(`equipment_types.${equipment.equipment_type.label}.LABEL`) }}
          {{
            equipment.equipment_type.is_active
              ? ''
              : `(${$t('common.INACTIVE')})`
          }}
        </span>
      </dd>
      <dt>{{ $t('common.DESCRIPTION') }}</dt>
      <dd>
        <span class="equipment-description" v-if="equipment.description">
          {{ equipment.description }}
        </span>
        <span v-else class="no-description">
          {{ $t('common.NO_DESCRIPTION') }}
        </span>
      </dd>
      <dt>{{ capitalize($t('workouts.WORKOUT', 0)) }}</dt>
      <dd>
        <router-link
          :to="`/workouts?equipment_id=${equipment.id}`"
          v-if="equipment.workouts_count"
        >
          {{ equipment.workouts_count }}
        </router-link>
        <template v-else>{{ equipment.workouts_count }}</template>
      </dd>
      <dt>{{ capitalize($t('workouts.TOTAL_DISTANCE', 0)) }}</dt>
      <dd>
        <Distance
          :distance="equipment.total_distance"
          unitFrom="km"
          :digits="2"
          :displayUnit="false"
          :useImperialUnits="authUser.imperial_units"
        />
        <span>
          {{ authUser.imperial_units ? 'miles' : 'km' }}
        </span>
      </dd>
      <dt>{{ capitalize($t('workouts.TOTAL_DURATION', 0)) }}</dt>
      <dd>
        {{ getTotalDuration(equipment.total_moving, $t) }}
        <template v-if="equipment.total_duration !== equipment.total_moving">
          (<span class="duration-detail">
            {{ $t('common.TOTAL_DURATION_WITH_PAUSES') }}:
          </span>
          {{ getTotalDuration(equipment.total_duration, $t) }})
        </template>
      </dd>
      <dt>{{ capitalize($t('common.ACTIVE', 0)) }}</dt>
      <dd>
        <i
          :class="`fa fa-${equipment.is_active ? 'check-' : ''}square-o`"
          aria-hidden="true"
        />
      </dd>
      <template v-if="equipment.default_for_sport_ids.length > 0">
        <dt>{{ capitalize($t('equipments.DEFAULT_FOR_SPORTS', 0)) }}</dt>
        <dd class="sports-list">
          <span
            class="sport-badge"
            :class="{ inactive: !sport.is_active_for_user }"
            v-for="sport in equipmentTranslatedSports"
            :key="sport.label"
          >
            <SportImage
              :title="sport.translatedLabel"
              :sport-label="sport.label"
              :color="sport.color ? sport.color : sportColors[sport.label]"
            />
            <router-link
              :to="`/profile/sports/${sport.id}?fromEquipmentId=${equipment.id}`"
            >
              {{ sport.translatedLabel }}
              {{ sport.is_active_for_user ? '' : `(${$t('common.INACTIVE')})` }}
            </router-link>
          </span>
        </dd>
      </template>
    </dl>
    <div class="equipment-buttons">
      <button
        @click="$router.push(`/profile/edit/equipments/${equipment.id}`)"
        :disabled="loading"
      >
        {{ $t('buttons.EDIT') }}
      </button>
      <button :disabled="loading" @click="refreshTotals(equipment.id)">
        {{ $t('buttons.REFRESH_TOTALS') }}
      </button>
      <button class="danger" @click="displayModal = true" :disabled="loading">
        {{ $t('buttons.DELETE') }}
      </button>
      <button
        :disabled="loading"
        @click="
          $router.push(
            route.query.fromWorkoutId
              ? `/workouts/${route.query.fromWorkoutId}`
              : route.query.fromSportId
                ? `/profile/sports/${route.query.fromSportId}`
                : '/profile/equipments'
          )
        "
      >
        {{ $t('buttons.BACK') }}
      </button>
    </div>
  </div>
  <div v-else>
    <p class="no-equipment">{{ $t('equipments.NO_EQUIPMENT') }}</p>
    <button @click="$router.push('/profile/equipments')" :disabled="loading">
      {{ $t('buttons.BACK') }}
    </button>
  </div>
</template>

<script setup lang="ts">
  import {
    capitalize,
    computed,
    inject,
    onBeforeMount,
    onUnmounted,
    ref,
    toRefs,
  } from 'vue'
  import type { ComputedRef, Ref } from 'vue'
  import { useI18n } from 'vue-i18n'
  import { useRoute } from 'vue-router'

  import { EQUIPMENTS_STORE, ROOT_STORE, SPORTS_STORE } from '@/store/constants'
  import type { IDeleteEquipmentPayload, IEquipment } from '@/types/equipments'
  import type { ISport, ITranslatedSport } from '@/types/sports'
  import type { IAuthUserProfile } from '@/types/user'
  import { useStore } from '@/use/useStore'
  import { getTotalDuration } from '@/utils/duration'
  import { translateSports } from '@/utils/sports'

  interface Props {
    authUser: IAuthUserProfile
    equipments: IEquipment[]
  }
  const props = defineProps<Props>()

  const store = useStore()
  const route = useRoute()
  const { t } = useI18n()

  const { authUser, equipments } = toRefs(props)

  const sportColors = inject('sportColors') as Record<string, string>
  const loading: ComputedRef<boolean> = computed(
    () => store.getters[EQUIPMENTS_STORE.GETTERS.LOADING]
  )
  const equipment: ComputedRef<IEquipment | null> = computed(() =>
    getEquipment(equipments.value)
  )
  const sports: ComputedRef<ISport[]> = computed(
    () => store.getters[SPORTS_STORE.GETTERS.SPORTS]
  )
  const equipmentTranslatedSports: ComputedRef<ITranslatedSport[]> = computed(
    () =>
      translateSports(
        sports.value,
        t,
        'all',
        authUser.value.sports_list
      ).filter((s) =>
        equipment.value
          ? equipment.value?.default_for_sport_ids.includes(s.id)
          : false
      )
  )
  const displayModal: Ref<boolean> = ref(false)

  onBeforeMount(() => {
    store.dispatch(EQUIPMENTS_STORE.ACTIONS.GET_EQUIPMENTS)
  })

  function getEquipment(equipmentsList: IEquipment[]) {
    if (!route.params.id) {
      return null
    }
    const filteredEquipmentList = equipmentsList.filter((equipment) =>
      route.params.id ? equipment.id === route.params.id : null
    )
    if (filteredEquipmentList.length === 0) {
      return null
    }
    return filteredEquipmentList[0]
  }
  function updateDisplayModal(display: boolean) {
    displayModal.value = display
  }
  function deleteEquipment() {
    if (equipment.value?.id) {
      const payload: IDeleteEquipmentPayload = { id: equipment.value.id }
      if (equipment.value?.workouts_count > 0) {
        payload.force = true
      }
      store.dispatch(EQUIPMENTS_STORE.ACTIONS.DELETE_EQUIPMENT, payload)
    }
  }
  function refreshTotals(equipmentId: string) {
    store.dispatch(EQUIPMENTS_STORE.ACTIONS.REFRESH_EQUIPMENT, equipmentId)
  }

  onUnmounted(() => {
    store.commit(ROOT_STORE.MUTATIONS.EMPTY_ERROR_MESSAGES)
  })
</script>

<style scoped lang="scss">
  @import '~@/scss/vars.scss';

  #user-equipment {
    .no-equipment {
      font-style: italic;
      padding: $default-padding 0;
    }
    .no-description {
      font-style: italic;
    }
    .equipment-description {
      white-space: pre-wrap;
    }
    .equipment-type {
      display: flex;
      .equipment-type-img {
        height: 25px;
        width: 25px;
        margin: 0;
      }
    }
    .sports-list {
      display: flex;
      gap: $default-padding;
      flex-wrap: wrap;
      padding-top: $default-padding * 0.5;
      .sport-badge {
        display: flex;
        gap: $default-padding;
        border: solid 1px var(--card-border-color);
        border-radius: $border-radius;
        padding: $default-padding * 0.75 $default-padding * 1.2;
        &.inactive {
          font-style: italic;
        }
        .sport-img {
          height: 20px;
          width: 20px;
          margin: 0;
        }
      }
    }
    .duration-detail {
      font-style: italic;
    }
  }
  .equipment-buttons {
    display: flex;
    flex-wrap: wrap;
    gap: $default-padding;
  }
</style>
