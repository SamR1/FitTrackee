<template>
  <div class="records-card">
    <Card>
      <template #title>
        <SportImage :sport-label="records.label" :color="records.color" />
        {{ sportTranslatedLabel }}
      </template>
      <template #content>
        <SportRecordsTable
          :class="{ 'max-width': maxWidth }"
          v-for="record in getTranslatedRecords(records.records)"
          :record="record"
          :key="record.id"
        />
      </template>
    </Card>
  </div>
</template>

<script setup lang="ts">
  import { computed, toRefs } from 'vue'
  import type { ComputedRef } from 'vue'
  import { useI18n } from 'vue-i18n'

  import SportRecordsTable from '@/components/Common/SportRecordsTable.vue'
  import { ROOT_STORE } from '@/store/constants'
  import type { ICardRecord, IRecord, IRecordsBySport } from '@/types/workouts'
  import { useStore } from '@/use/useStore'
  import { sortRecords } from '@/utils/records'

  interface Props {
    records: IRecordsBySport
    sportTranslatedLabel: string
  }
  const props = defineProps<Props>()

  const { records, sportTranslatedLabel } = toRefs(props)

  const store = useStore()
  const { t } = useI18n()

  const language: ComputedRef<string> = computed(
    () => store.getters[ROOT_STORE.GETTERS.LANGUAGE]
  )
  const maxWidth: ComputedRef<boolean> = computed(() => language.value === 'bg')

  function getTranslatedRecords(records: IRecord[]): ICardRecord[] {
    const translatedRecords: ICardRecord[] = []
    records.map((record) => {
      translatedRecords.push({
        ...record,
        label: t(`workouts.RECORD_${record.record_type}`),
      })
    })
    return translatedRecords.sort(sortRecords)
  }
</script>

<style lang="scss" scoped>
  @import '~@/scss/vars.scss';

  .records-card {
    width: 100%;
    padding-bottom: $default-padding * 0.3;

    ::v-deep(.card) {
      font-size: 0.9em;
      .card-title {
        display: flex;
        font-size: 0.9em;
        .sport-img {
          padding-right: $default-padding;
          height: 20px;
          width: 20px;
        }
      }
      .card-content {
        font-size: 0.9em;
        padding: $default-padding;
        .record {
          display: flex;
          align-items: center;
          justify-content: space-between;
          span {
            padding: 2px;
          }
          .record-type {
            flex-grow: 1;
          }
          .record-value {
            font-weight: bold;
            white-space: nowrap;
            padding-right: $default-padding;
          }
          .record-date {
            white-space: nowrap;
            min-width: 30%;
            text-align: right;
          }
        }
      }
      @media screen and (max-width: $medium-limit) {
        font-size: 1em;
        .card-title {
          font-size: 1em;
          .sport-img {
            height: 22px;
            width: 22px;
          }
        }
      }
      @media screen and (max-width: $x-small-limit) {
        .card-content {
          .record.max-width {
            .record-type {
              max-width: 40%;
            }
          }
        }
      }
    }
  }
</style>
