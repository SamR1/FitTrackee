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
      <dt>{{ capitalize($t('visibility_levels.VISIBILITY')) }}</dt>
      <dd>
        {{ $t(`visibility_levels.LEVELS.${equipment.visibility}`) }}
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
          <SportBadge
            v-for="sport in equipmentTranslatedSports"
            :key="sport.label"
            :sport="sport"
            :from="`?fromEquipmentId=${equipment.id}`"
          />
        </dd>
      </template>
    </dl>
    <ErrorMessage :message="errorMessages" v-if="errorMessages" />
    <div class="equipment-buttons">
      <template v-if="!authUser.suspended_at">
        <button
          @click="$router.push(`/profile/edit/equipments/${equipment.id}`)"
          :disabled="equipmentsLoading"
        >
          {{ $t('buttons.EDIT') }}
        </button>
        <button
          :disabled="equipmentsLoading"
          @click="refreshTotals(equipment.id)"
        >
          {{ $t('buttons.REFRESH_TOTALS') }}
        </button>
        <button
          class="danger"
          @click="displayModal = true"
          :disabled="equipmentsLoading"
        >
          {{ $t('buttons.DELETE') }}
        </button>
      </template>
      <button
        :disabled="equipmentsLoading"
        @click="
          $router.push(
            $route.query.fromWorkoutId
              ? `/workouts/${$route.query.fromWorkoutId}`
              : $route.query.fromSportId
                ? `/profile/sports/${$route.query.fromSportId}`
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
    <button
      @click="$router.push('/profile/equipments')"
      :disabled="equipmentsLoading"
    >
      {{ $t('buttons.BACK') }}
    </button>
  </div>
</template>

<script setup lang="ts">
  import { capitalize, computed, onBeforeMount, ref, toRefs } from 'vue'
  import type { ComputedRef, Ref } from 'vue'
  import { useI18n } from 'vue-i18n'

  import SportBadge from '@/components/Common/SportBadge.vue'
  import useApp from '@/composables/useApp'
  import useEquipments from '@/composables/useEquipments'
  import useSports from '@/composables/useSports'
  import { EQUIPMENTS_STORE } from '@/store/constants'
  import type { IDeleteEquipmentPayload } from '@/types/equipments'
  import type { ITranslatedSport } from '@/types/sports'
  import type { IAuthUserProfile } from '@/types/user'
  import { useStore } from '@/use/useStore'
  import { getTotalDuration } from '@/utils/duration'
  import { translateSports } from '@/utils/sports'

  interface Props {
    authUser: IAuthUserProfile
    equipmentsLoading: boolean
  }
  const props = defineProps<Props>()
  const { authUser } = toRefs(props)

  const store = useStore()
  const { t } = useI18n()

  const { errorMessages } = useApp()
  const { equipment } = useEquipments()
  const { sports } = useSports()

  const displayModal: Ref<boolean> = ref(false)

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

  onBeforeMount(() => {
    store.dispatch(EQUIPMENTS_STORE.ACTIONS.GET_EQUIPMENTS)
  })
</script>

<style scoped lang="scss">
  @use '~@/scss/vars.scss' as *;

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
  .error-message {
    margin: $default-margin * 2 0;
  }
</style>
