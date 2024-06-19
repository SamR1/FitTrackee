<template>
  <div class="record">
    <span class="record-type">
      {{ capitalize(record.label) }}
    </span>
    <span class="record-value">{{ record.value }}</span>
    <span class="record-date">
      <router-link
        :to="{
          name: 'Workout',
          params: { workoutId: record.workout_id },
        }"
      >
        <time>{{ record.workout_date }}</time>
      </router-link>
    </span>
  </div>
</template>

<script setup lang="ts">
  import { capitalize, toRefs } from 'vue'

  import type { ICardRecord } from '@/types/workouts'

  interface Props {
    record: ICardRecord
  }
  const props = defineProps<Props>()

  const { record } = toRefs(props)
</script>

<style lang="scss" scoped>
  @import '~@/scss/vars.scss';

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
</style>
