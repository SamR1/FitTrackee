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
          <i class="fa fa-chevron-left" aria-hidden="true" />
          {{ $t('api.PAGINATION.PREVIOUS') }}
        </router-link>
      </li>
      <li
        v-for="page in rangePagination(pagination.pages, pagination.page)"
        :key="page"
        class="page"
        :class="{ active: page === pagination.page }"
      >
        <span v-if="page === '...'"> ... </span>
        <router-link
          v-else
          class="page-link"
          :to="{ path, query: getQuery(+page) }"
        >
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
          <i class="fa fa-chevron-right" aria-hidden="true" />
        </router-link>
      </li>
    </ul>
  </nav>
</template>

<script setup lang="ts">
  import { toRefs } from 'vue'

  import { IPagination } from '@/types/api'
  import { TWorkoutsPayload } from '@/types/workouts'
  import { rangePagination } from '@/utils/api'

  interface Props {
    pagination: IPagination
    path: string
    query: TWorkoutsPayload
  }
  const props = defineProps<Props>()

  const { pagination, path, query } = toRefs(props)

  function getQuery(page: number, cursor?: number): TWorkoutsPayload {
    const newQuery = Object.assign({}, query.value)
    newQuery.page = cursor ? page + cursor : page
    return newQuery
  }
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
      .fa {
        font-size: 0.8em;
        padding: 0 $default-padding * 0.5;
      }
    }

    @media screen and (max-width: $medium-limit) {
      .pagination {
        .page {
          display: none;
        }
      }
    }
  }
</style>
