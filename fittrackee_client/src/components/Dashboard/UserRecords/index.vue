<template>
  <div class="user-records-section">
    <div class="section-title">
      <i class="fa fa-trophy custom-fa-small" aria-hidden="true" />
      <span class="title">{{ $t('workouts.RECORD', 2) }}</span>
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
  import { computed, toRefs } from 'vue'
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
  const { user } = toRefs(props)

  const { t } = useI18n()

  const recordsBySport = computed(() =>
    getRecordsBySports(
      user.value.records,
      translateSports(props.sports, t),
      user.value.timezone,
      user.value.imperial_units,
      user.value.display_ascent,
      user.value.date_format
    )
  )
</script>

<style lang="scss" scoped>
  @use '~@/scss/vars.scss' as *;

  .user-records {
    .no-records {
      border: solid 1px var(--card-border-color);
      border-radius: $border-radius;
      padding: $default-padding;
      margin: $default-margin;
    }
  }
</style>
