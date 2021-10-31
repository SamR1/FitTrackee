<template>
  <div class="table-selects">
    <label>
      {{ $t('admin.USERS.SELECTS.ORDER_BY.LABEL') }}:
      <select
        name="order_by"
        id="order_by"
        :value="query.order_by"
        @change="onSelectUpdate"
      >
        <option v-for="order in order_by" :value="order" :key="order">
          {{ $t(`admin.USERS.SELECTS.ORDER_BY.${order}`) }}
        </option>
      </select>
    </label>
    <label>
      {{ $t('admin.USERS.SELECTS.ORDER.LABEL') }}:
      <select
        name="order"
        id="order"
        :value="query.order"
        @change="onSelectUpdate"
      >
        <option v-for="order in sort" :value="order" :key="order">
          {{ $t(`admin.USERS.SELECTS.ORDER.${order.toUpperCase()}`) }}
        </option>
      </select>
    </label>
    <label>
      {{ $t('admin.USERS.SELECTS.PER_PAGE.LABEL') }}:
      <select
        name="per_page"
        id="per_page"
        :value="query.per_page"
        @change="onSelectUpdate"
      >
        <option v-for="nb in per_page" :value="nb" :key="nb">
          {{ nb }}
        </option>
      </select>
    </label>
  </div>
</template>

<script lang="ts">
  import { PropType, defineComponent } from 'vue'

  import { TPaginationPayload } from '@/types/api'

  export default defineComponent({
    name: 'AdminUsersSelects',
    props: {
      order_by: {
        type: Object as PropType<string[]>,
        required: true,
      },
      query: {
        type: Object as PropType<TPaginationPayload>,
        required: true,
      },
      sort: {
        type: Object as PropType<string[]>,
        required: true,
      },
    },
    emits: ['updateSelect'],
    setup(props, { emit }) {
      function onSelectUpdate(event: Event & { target: HTMLInputElement }) {
        emit('updateSelect', event.target.id, event.target.value)
      }

      return {
        per_page: [10, 50, 100],
        onSelectUpdate,
      }
    },
  })
</script>

<style lang="scss" scoped>
  @import '~@/scss/base.scss';

  .table-selects {
    display: flex;
    justify-content: space-between;
    margin: $default-margin 0;

    label {
      select {
        margin-left: $default-margin;
        padding: $default-padding * 0.5;
      }
    }

    @media screen and (max-width: $small-limit) {
      flex-wrap: wrap;
      label {
        margin-bottom: $default-margin;
        select {
          margin-left: 0;
        }
      }
    }
  }
</style>
