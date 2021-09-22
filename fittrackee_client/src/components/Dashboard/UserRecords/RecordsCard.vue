<template>
  <div class="records-card">
    <Card :without-title="false">
      <template #title>
        <div>
          <img
            class="sport-img"
            :alt="`${sportLabel} logo`"
            :src="records.img"
          />
        </div>
        {{ sportLabel }}
      </template>
      <template #content>
        <div class="record" v-for="record in records.records" :key="record.id">
          <span class="record-type">{{
            t(`workouts.RECORD_${record.record_type}`)
          }}</span>
          <span class="record-value">{{ record.value }}</span>
          <span class="record-date">{{ record.workout_date }}</span>
        </div>
      </template>
    </Card>
  </div>
</template>

<script lang="ts">
  import { PropType, defineComponent } from 'vue'
  import { useI18n } from 'vue-i18n'

  import Card from '@/components/Common/Card.vue'
  import { IRecord } from '@/types/workouts'

  export default defineComponent({
    name: 'RecordsCard',
    components: {
      Card,
    },
    props: {
      records: {
        type: Object as PropType<IRecord[]>,
        required: true,
      },
      sportLabel: {
        type: String,
        required: true,
      },
    },
    setup() {
      const { t } = useI18n()
      return { t }
    },
  })
</script>

<style lang="scss" scoped>
  @import '~@/scss/base';

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
          height: 18px;
          width: 18px;
        }
      }
      .card-content {
        font-size: 0.9em;
        padding: $default-padding;
        .record {
          display: flex;
          justify-content: space-between;
          span {
            padding: 2px 5px;
          }
          .record-type {
            flex-grow: 1;
          }
          .record-value {
            font-weight: bold;
            padding-right: $default-padding * 2;
          }
        }
      }
    }
  }
</style>
