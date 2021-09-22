<template>
  <div class="user-records">
    <Card v-if="Object.keys(recordsBySport).length === 0" class="no-records">
      <template #content>{{ t('workouts.NO_RECORDS') }}</template>
    </Card>
    <RecordsCard
      v-for="sportLabel in Object.keys(recordsBySport).sort()"
      :sportLabel="sportLabel"
      :records="recordsBySport[sportLabel]"
      :key="sportLabel"
    />
  </div>
</template>

<script lang="ts">
  import { computed, defineComponent, PropType } from 'vue'
  import { useI18n } from 'vue-i18n'

  import Card from '@/components/Common/Card.vue'
  import RecordsCard from '@/components/Dashboard/UserRecords/RecordsCard.vue'
  import { SPORTS_STORE } from '@/store/constants'
  import { IAuthUserProfile } from '@/types/user'
  import { useStore } from '@/use/useStore'
  import { getRecordsBySports } from '@/utils/records'
  import { translateSports } from '@/utils/sports'

  export default defineComponent({
    name: 'UserRecords',
    components: {
      Card,
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
    display: flex;
    flex-wrap: wrap;
    justify-content: space-between;

    .no-records {
      width: 100%;
    }
  }
</style>
