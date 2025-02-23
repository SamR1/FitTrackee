<template>
  <div id="user-sport-preferences">
    <Modal
      v-if="displayModal"
      :title="$t('common.CONFIRMATION')"
      :message="
        $t(
          `user.PROFILE.SPORT.CONFIRM_SPORT_RESET${hasEquipments ? '_WITH_EQUIPMENTS' : ''}`
        )
      "
      @confirmAction="resetSport(sportPayload.sport_id)"
      @cancelAction="updateDisplayModal(false)"
      @keydown.esc="updateDisplayModal(false)"
    />
    <div class="responsive-table" v-if="translatedSports.length > 0">
      <div class="mobile-display">
        <div v-if="isEdition" class="profile-buttons mobile-display">
          <button
            class="cancel"
            @click.prevent="$router.push('/profile/sports')"
          >
            {{ $t('buttons.BACK') }}
          </button>
        </div>
        <div v-else class="profile-buttons">
          <button @click="$router.push('/profile/edit/sports')">
            {{ $t('user.PROFILE.EDIT_SPORTS_PREFERENCES') }}
          </button>
          <button @click="$router.push('/')">{{ $t('common.HOME') }}</button>
        </div>
      </div>
      <table>
        <thead>
          <tr>
            <th>{{ $t('user.PROFILE.SPORT.COLOR') }}</th>
            <th class="text-left">{{ $t('workouts.SPORT', 0) }}</th>
            <th>{{ $t('workouts.WORKOUT', 0) }}</th>
            <th>{{ $t('equipments.EQUIPMENT', 0) }}</th>
            <th>{{ $t('user.PROFILE.SPORT.IS_ACTIVE') }}</th>
            <th>
              <div class="threshold">
                <span>
                  {{ $t('user.PROFILE.SPORT.STOPPED_SPEED_THRESHOLD') }}
                </span>
                <span>
                  ({{ `${authUser.imperial_units ? 'mi' : 'km'}/h` }})
                </span>
              </div>
            </th>
            <th v-if="isEdition && !authUser.suspended_at">
              {{ $t('user.PROFILE.SPORT.ACTION') }}
            </th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="sport in translatedSports" :key="sport.id">
            <td>
              <span class="cell-heading">
                {{ $t('user.PROFILE.SPORT.COLOR') }}
              </span>
              <input
                v-if="isSportInEdition(sport.id)"
                class="sport-color"
                type="color"
                v-model="sportPayload.color"
              />
              <SportImage
                v-else
                :title="sport.translatedLabel"
                :sport-label="sport.label"
                :color="sport.color ? sport.color : sportColors[sport.label]"
              />
            </td>
            <td
              class="sport-label"
              :class="{ 'disabled-sport': !sport.is_active }"
            >
              <span class="cell-heading">
                {{ $t('user.PROFILE.SPORT.LABEL') }}
              </span>
              <template v-if="isSportInEdition(sport.id)">
                {{ sport.translatedLabel }}
              </template>
              <router-link v-else :to="`/profile/sports/${sport.id}`">
                {{ sport.translatedLabel }}
              </router-link>
              <span class="disabled-message" v-if="!sport.is_active">
                ({{ $t('user.PROFILE.SPORT.DISABLED_BY_ADMIN') }})
              </span>
              <i
                v-if="authUserLoading && isSportInEdition(sport.id)"
                class="fa fa-refresh fa-spin fa-fw"
              />
              <ErrorMessage
                :message="errorMessages"
                v-if="errorMessages && sportPayload.sport_id === sport.id"
              />
            </td>
            <td
              class="text-center"
              :class="{ 'disabled-sport': !sport.is_active }"
            >
              <span class="cell-heading">
                {{ $t('workouts.WORKOUT', 0) }}
              </span>
              <i
                :class="`fa fa${
                  authUser.sports_list.includes(sport.id) ? '-check' : ''
                }`"
                aria-hidden="true"
              />
            </td>
            <td
              class="text-center"
              :class="{ 'disabled-sport': !sport.is_active }"
            >
              <span class="cell-heading">
                {{ $t('equipments.EQUIPMENT', 0) }}
              </span>
              <i
                :class="`fa fa${sport.default_equipments.length > 0 ? '-check' : ''}`"
                aria-hidden="true"
              />
            </td>
            <td
              class="text-center"
              :class="{ 'disabled-sport': !sport.is_active }"
            >
              <span class="cell-heading">
                {{ $t('user.PROFILE.SPORT.IS_ACTIVE') }}
              </span>
              <input
                v-if="isSportInEdition(sport.id) && sport.is_active"
                type="checkbox"
                :checked="sport.is_active_for_user"
                @change="updateIsActive"
              />
              <i
                v-else
                :class="`fa fa${sport.is_active_for_user ? '-check' : ''}`"
                aria-hidden="true"
              />
            </td>
            <td
              class="text-center"
              :class="{ 'disabled-sport': !sport.is_active }"
            >
              <span class="cell-heading">
                {{ $t('user.PROFILE.SPORT.STOPPED_SPEED_THRESHOLD') }}
                {{ `${authUser.imperial_units ? 'mi' : 'km'}/h` }}
              </span>
              <input
                class="threshold-input"
                v-if="isSportInEdition(sport.id) && sport.is_active"
                type="number"
                min="0"
                step="0.1"
                v-model="sportPayload.stopped_speed_threshold"
              />
              <span v-else>
                <Distance
                  :distance="sport.stopped_speed_threshold"
                  unitFrom="km"
                  :speed="true"
                  :useImperialUnits="authUser.imperial_units"
                  :displayUnit="false"
                />
              </span>
            </td>
            <td
              v-if="isEdition && !authUser.suspended_at"
              class="action-buttons"
            >
              <span class="cell-heading">
                {{ $t('user.PROFILE.SPORT.ACTION') }}
              </span>
              <button
                v-if="sportPayload.sport_id === 0"
                @click="updateSportInEdition(sport)"
              >
                {{ $t('buttons.EDIT') }}
              </button>
              <div v-if="isSportInEdition(sport.id)" class="edition-buttons">
                <button
                  :disabled="authUserLoading"
                  @click.prevent="updateSport(authUser)"
                >
                  {{ $t('buttons.SUBMIT') }}
                </button>
                <button
                  :disabled="authUserLoading"
                  class="warning"
                  @click.prevent="updateDisplayModal(true)"
                >
                  {{ $t('buttons.RESET') }}
                </button>
                <button
                  :disabled="authUserLoading"
                  @click="updateSportInEdition(null)"
                >
                  {{ $t('buttons.CANCEL') }}
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
      <div v-if="isEdition" class="profile-buttons">
        <button class="cancel" @click.prevent="$router.push('/profile/sports')">
          {{ $t('buttons.BACK') }}
        </button>
      </div>
      <div v-else class="profile-buttons">
        <button
          v-if="!authUser.suspended_at"
          @click="$router.push('/profile/edit/sports')"
        >
          {{ $t('user.PROFILE.EDIT_SPORTS_PREFERENCES') }}
        </button>
        <button @click="$router.push('/')">{{ $t('common.HOME') }}</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
  import { ref, toRefs, watch } from 'vue'
  import type { Ref } from 'vue'

  import useApp from '@/composables/useApp'
  import useAuthUser from '@/composables/useAuthUser'
  import useSports from '@/composables/useSports'
  import { ROOT_STORE } from '@/store/constants'
  import type { ISport, ITranslatedSport } from '@/types/sports'
  import type { IAuthUserProfile } from '@/types/user'
  import { useStore } from '@/use/useStore'
  import { convertDistance } from '@/utils/units'

  interface Props {
    authUser: IAuthUserProfile
    translatedSports: ITranslatedSport[]
    isEdition: boolean
  }
  const props = defineProps<Props>()
  const { authUser, isEdition, translatedSports } = toRefs(props)

  const store = useStore()

  const { errorMessages } = useApp()
  const {
    defaultColor,
    displayModal,
    sportColors,
    sportPayload,
    resetSport,
    updateDisplayModal,
    updateIsActive,
    updateSport,
  } = useSports()
  const { authUserLoading } = useAuthUser()

  const hasEquipments: Ref<boolean> = ref(false)

  function updateSportInEdition(sport: ISport | null) {
    if (sport !== null) {
      sportPayload.sport_id = sport.id
      sportPayload.color = sport.color
        ? sport.color
        : sportColors
          ? sportColors[sport.label]
          : defaultColor
      sportPayload.is_active = sport.is_active_for_user
      sportPayload.stopped_speed_threshold = +`${
        authUser.value.imperial_units
          ? convertDistance(sport.stopped_speed_threshold, 'km', 'mi', 2)
          : parseFloat(sport.stopped_speed_threshold.toFixed(2))
      }`
      hasEquipments.value = sport.default_equipments.length > 0
    } else {
      resetSportPayload()
    }
  }
  function isSportInEdition(sportId: number) {
    return sportPayload.sport_id === sportId
  }
  function resetSportPayload() {
    sportPayload.sport_id = 0
    sportPayload.color = null
    sportPayload.is_active = true
    sportPayload.stopped_speed_threshold = 1
    hasEquipments.value = false
    store.commit(ROOT_STORE.MUTATIONS.EMPTY_ERROR_MESSAGES)
  }

  watch(
    () => authUserLoading.value,
    (newIsLoading) => {
      if (!newIsLoading && !errorMessages.value) {
        resetSportPayload()
        updateDisplayModal(false)
      }
    }
  )
</script>

<style lang="scss" scoped>
  @use '~@/scss/vars.scss' as *;
  #user-sport-preferences {
    table {
      th {
        padding-top: 0;
        text-transform: lowercase;
      }
    }
    .sport-img {
      height: 35px;
      width: 35px;
      margin: 0 auto;
    }
    .sport-color {
      border: none;
      margin: 6px 1px 6px 0;
      padding: 0;
      width: 40px;
    }
    .sport-label {
      width: 170px;
    }
    .disabled-sport {
      font-style: italic;
      color: var(--disabled-sport-color);

      .disabled-message {
        font-size: 0.9em;
      }
      .cell-heading {
        font-style: normal;
      }
    }
    .profile-buttons {
      display: flex;
      align-items: center;
      flex-wrap: wrap;
    }
    .action-buttons {
      width: 70px;
    }
    .edition-buttons {
      display: flex;
      flex-wrap: wrap;
      gap: $default-padding * 0.5;
      line-height: 1.3em;

      button {
        text-align: center;
        min-width: 80px;
      }
    }
    .threshold {
      display: flex;
      flex-direction: column;
      hyphens: auto;
      min-width: 100px;
    }
    .threshold-input {
      padding: $default-padding * 0.5;
      width: 50px;
    }
    .mobile-display {
      display: none;
    }
    div.error-message {
      margin: 0;
    }

    @media screen and (max-width: $small-limit) {
      .sport-label,
      .action-buttons {
        width: 45%;
      }
      .edition-buttons {
        justify-content: center;
      }
      .mobile-display {
        display: flex;
        margin: $default-margin 0 $default-margin;
      }
    }
    @media screen and (max-width: $x-small-limit) {
      .sport-label,
      .action-buttons {
        width: 100%;
      }
    }
  }
</style>
