<template>
  <div class="table-selects">
    <label>
      {{ $t('common.SELECTS.ORDER_BY.LABEL') }}:
      <select
        name="order_by"
        id="order_by"
        :value="query.order_by"
        @change="onSelectUpdate"
      >
        <option v-for="order in order_by" :value="order" :key="order">
          {{ $t(`${message}.${order.toUpperCase()}`) }}
        </option>
      </select>
    </label>
    <label>
      {{ $t('common.SELECTS.ORDER.LABEL') }}:
      <select
        name="order"
        id="order"
        :value="query.order"
        @change="onSelectUpdate"
      >
        <option v-for="order in sort" :value="order" :key="order">
          {{ $t(`common.SELECTS.ORDER.${order.toUpperCase()}`) }}
        </option>
      </select>
    </label>
    <slot name="additionalFilters"></slot>
    <label>
      {{ $t('common.SELECTS.PER_PAGE.LABEL') }}:
      <select
        name="per_page"
        id="per_page"
        :value="query.per_page"
        @change="onSelectUpdate"
      >
        <option v-for="nb in perPage" :value="nb" :key="nb">
          {{ nb }}
        </option>
      </select>
    </label>
  </div>
</template>

<script setup lang="ts">
  import { toRefs } from 'vue'

  import type { TPaginationPayload } from '@/types/api'

  interface Props {
    order_by: string[]
    query: TPaginationPayload
    sort: string[]
    message: string
  }
  const props = defineProps<Props>()
  const { order_by, query, sort, message } = toRefs(props)

  const emit = defineEmits(['updateSelect'])

  const perPage = [10, 25, 50, 100]

  function onSelectUpdate(event: Event) {
    emit(
      'updateSelect',
      (event.target as HTMLInputElement).id,
      (event.target as HTMLInputElement).value
    )
  }
</script>
