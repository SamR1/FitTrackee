<template>
  <nav class="pagination-center" aria-label="navigation">
    <ul class="pagination">
      <li class="page-prev" :class="{ disabled: !pagination.has_prev }">
        <router-link
          class="page-link"
          :to="{ path, query: getQuery(pagination.page, -1) }"
          :event="pagination.has_prev ? 'click' : ''"
          :disabled="!pagination.has_prev"
        >
          {{ $t('api.PAGINATION.PREVIOUS') }}
        </router-link>
      </li>
      <li
        v-for="page in rangePagination(pagination.pages)"
        :key="page"
        class="page"
        :class="{ active: page === pagination.page }"
      >
        <router-link class="page-link" :to="{ path, query: getQuery(page) }">
          {{ page }}
        </router-link>
      </li>
      <li class="page-next" :class="{ disabled: !pagination.has_next }">
        <router-link
          class="page-link"
          :to="{ path, query: getQuery(pagination.page, 1) }"
          :event="pagination.has_next ? 'click' : ''"
          :disabled="!pagination.has_next"
        >
          {{ $t('api.PAGINATION.NEXT') }}
        </router-link>
      </li>
    </ul>
  </nav>
</template>

<script lang="ts">
  import { PropType, defineComponent } from 'vue'

  import { IPagination, IPaginationPayload } from '@/types/api'

  export default defineComponent({
    name: 'Pagination',
    props: {
      pagination: {
        type: Object as PropType<IPagination>,
        required: true,
      },
      path: {
        type: String,
        required: true,
      },
      query: {
        type: Object as PropType<IPaginationPayload>,
        required: true,
      },
    },
    setup(props) {
      function rangePagination(pages: number): number[] {
        return Array.from({ length: pages }, (_, i) => i + 1)
      }
      function getQuery(page: number, cursor?: number): IPaginationPayload {
        const newQuery = Object.assign({}, props.query)
        newQuery.page = cursor ? page + cursor : page
        return newQuery
      }
      return { rangePagination, getQuery }
    },
  })
</script>

<style lang="scss" scoped>
  @import '~@/scss/base.scss';

  .pagination-center {
    display: flex;
    justify-content: center;
    font-size: 0.9em;

    .pagination {
      display: flex;
      padding-left: 0;
      list-style: none;
      border-radius: 0.25rem;

      .page-prev,
      .page-next,
      .page {
        border: solid 1px var(--card-border-color);
        padding: $default-padding $default-padding * 1.5;

        &.active {
          font-weight: bold;
        }

        &.disabled {
          cursor: default;
          a {
            color: var(--disabled-color);
          }
        }
      }

      .page {
        margin-left: -1px;
      }

      .page-prev {
        border-top-left-radius: 5px;
        border-bottom-left-radius: 5px;
      }
      .page-next {
        border-top-right-radius: 5px;
        border-bottom-right-radius: 5px;
        margin-left: -1px;
      }
    }
  }
</style>
