<template>
  <div class="user-records-section">
    <div class="section-title">
      <i class="fa fa-trophy custom-fa-small" aria-hidden="true" />
      {{ $t('workouts.RECORD', 2) }}
    </div>
    <div class="user-records">
      <div v-if="Object.keys(recordsBySport).length === 0" class="no-records">
        {{ $t('workouts.NO_RECORDS') }}
      </div>
      <RecordsCard
        v-for="sportTranslatedLabel in Object.keys(recordsBySport).sort()"
        :sportTranslatedLabel="sportTranslatedLabel"
        :records="recordsBySport[sportTranslatedLabel]"
        :key="sportTranslatedLabel"
        :useImperialUnits="user.imperial_units"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
  import { computed } from 'vue'
  import { useI18n } from 'vue-i18n'

  import RecordsCard from '@/components/Dashboard/UserRecords/RecordsCard.vue'
  import type { ISport } from '@/types/sports'
  import type { IAuthUserProfile } from '@/types/user'
  import { getRecordsBySports } from '@/utils/records'
  import { translateSports } from '@/utils/sports'

  interface Props {
    sports: ISport[]
    user: IAuthUserProfile
  }
  const props = defineProps<Props>()

  const { t } = useI18n()

  const recordsBySport = computed(() =>
    getRecordsBySports(
      props.user.records,
      translateSports(props.sports, t),
      props.user.timezone,
      props.user.imperial_units,
      props.user.display_ascent,
      props.user.date_format
    )
  )
</script>

<style lang="scss" scoped>
  @import '~@/scss/vars.scss';

  .user-records {
    .no-records {
      border: solid 1px var(--card-border-color);
      border-radius: $border-radius;
      padding: $default-padding;
      margin: $default-margin;
    }
  }
</style>
