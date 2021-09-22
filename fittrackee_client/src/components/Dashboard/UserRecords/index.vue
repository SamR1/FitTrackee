<template>
  <div class="user-records-section">
    <div class="section-title">
      <i class="fa fa-trophy custom-fa-small" aria-hidden="true" />
      {{ t('workouts.RECORD', 2) }}
    </div>
    <div class="user-records">
      <div v-if="Object.keys(recordsBySport).length === 0" class="no-records">
        {{ t('workouts.NO_RECORDS') }}
      </div>
      <RecordsCard
        v-for="sportLabel in Object.keys(recordsBySport).sort()"
        :sportLabel="sportLabel"
        :records="recordsBySport[sportLabel]"
        :key="sportLabel"
      />
    </div>
  </div>
</template>

<script lang="ts">
  import { computed, defineComponent, PropType } from 'vue'
  import { useI18n } from 'vue-i18n'

  import RecordsCard from '@/components/Dashboard/UserRecords/RecordsCard.vue'
  import { SPORTS_STORE } from '@/store/constants'
  import { IAuthUserProfile } from '@/types/user'
  import { useStore } from '@/use/useStore'
  import { getRecordsBySports } from '@/utils/records'
  import { translateSports } from '@/utils/sports'

  export default defineComponent({
    name: 'UserRecords',
    components: {
      RecordsCard,
    },
    props: {
      user: {
        type: Object as PropType<IAuthUserProfile>,
        required: true,
      },
    },
    setup(props) {
      const store = useStore()
      const { t } = useI18n()
      const recordsBySport = computed(() =>
        getRecordsBySports(
          props.user.records,
          translateSports(store.getters[SPORTS_STORE.GETTERS.SPORTS], t),
          props.user.timezone
        )
      )
      return { recordsBySport, t }
    },
  })
</script>

<style lang="scss" scoped>
  @import '~@/scss/base';

  .user-records {
    .no-records {
      padding: $default-padding;
    }
  }
</style>
