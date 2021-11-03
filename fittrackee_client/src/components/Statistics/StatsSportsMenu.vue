<template>
  <div class="sports-menu">
    <label
      v-for="sport in translatedSports"
      type="checkbox"
      :key="sport.id"
      :style="{ color: sportColors[sport.label] }"
    >
      <input
        type="checkbox"
        :id="sport.id"
        :name="sport.label"
        :checked="selectedSportIds.includes(sport.id)"
        @input="updateSelectedSportIds(sport.id)"
      />
      <SportImage :sport-label="sport.label" />
      <span class="sport-label">{{ sport.translatedLabel }}</span>
    </label>
  </div>
</template>

<script lang="ts">
  import { ComputedRef, PropType, computed, defineComponent, inject } from 'vue'
  import { useI18n } from 'vue-i18n'

  import { ISport, ITranslatedSport } from '@/types/sports'
  import { translateSports } from '@/utils/sports'

  export default defineComponent({
    name: 'SportsMenu',
    props: {
      selectedSportIds: {
        type: Array as PropType<number[]>,
        default: () => [],
      },
      userSports: {
        type: Object as PropType<ISport[]>,
        required: true,
      },
    },
    emits: ['selectedSportIdsUpdate'],
    setup(props, { emit }) {
      const { t } = useI18n()
      const translatedSports: ComputedRef<ITranslatedSport[]> = computed(() =>
        translateSports(props.userSports, t)
      )

      function updateSelectedSportIds(sportId: number) {
        emit('selectedSportIdsUpdate', sportId)
      }

      return {
        sportColors: inject('sportColors'),
        translatedSports,
        updateSelectedSportIds,
      }
    },
  })
</script>

<style lang="scss">
  @import '~@/scss/base.scss';
  .sports-menu {
    display: flex;
    justify-content: space-between;
    flex-wrap: wrap;
    padding: $default-padding;
    @media screen and (max-width: $medium-limit) {
      justify-content: normal;
    }

    label {
      display: flex;
      align-items: center;
      font-size: 0.9em;
      font-weight: normal;
      min-width: 120px;
      padding: $default-padding;
      @media screen and (max-width: $medium-limit) {
        min-width: 100px;
      }
      @media screen and (max-width: $x-small-limit) {
        min-width: 20px;
        .sport-label {
          display: none;
        }
      }
    }

    .sport-img {
      padding: 3px;
      width: 20px;
      height: 20px;
    }
  }
</style>
