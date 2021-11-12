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
      <SportImage :sport-label="sport.label" :color="sport.color" />
      <span class="sport-label">{{ sport.translatedLabel }}</span>
    </label>
  </div>
</template>

<script setup lang="ts">
  import { ComputedRef, computed, inject, withDefaults, toRefs } from 'vue'
  import { useI18n } from 'vue-i18n'

  import { ISport, ITranslatedSport } from '@/types/sports'
  import { translateSports } from '@/utils/sports'

  interface Props {
    userSports: ISport[]
    selectedSportIds?: number[]
  }
  const props = withDefaults(defineProps<Props>(), {
    selectedSportIds: () => [],
  })

  const emit = defineEmits(['selectedSportIdsUpdate'])

  const { t } = useI18n()

  const sportColors = inject('sportColors')
  const { selectedSportIds } = toRefs(props)
  const translatedSports: ComputedRef<ITranslatedSport[]> = computed(() =>
    translateSports(props.userSports, t)
  )

  function updateSelectedSportIds(sportId: number) {
    emit('selectedSportIdsUpdate', sportId)
  }
</script>

<style lang="scss">
  @import '~@/scss/base.scss';
  .sports-menu {
    display: flex;
    flex-wrap: wrap;
    padding: $default-padding;

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
