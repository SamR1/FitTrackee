<template>
  <nav class="pagination-center" aria-label="navigation">
    <ul class="pagination">
      <li class="page-prev" :class="{ disabled: !pagination.has_prev }">
        <router-link
          v-if="pagination.has_prev"
          class="page-link"
          :to="{ path, query: getQuery(pagination.page, -1) }"
        >
          {{ $t('common.PREVIOUS') }}
          <i class="fa fa-chevron-left" aria-hidden="true" />
        </router-link>
        <span v-else class="page-disabled-link">
          {{ $t('common.PREVIOUS') }}
        </span>
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
          v-if="pagination.has_next"
          class="page-link"
          :to="{ path, query: getQuery(pagination.page, 1) }"
        >
          {{ $t('common.NEXT') }}
          <i class="fa fa-chevron-right" aria-hidden="true" />
        </router-link>
        <span v-else class="page-disabled-link">
          {{ $t('common.NEXT') }}
        </span>
      </li>
    </ul>
  </nav>
</template>

<script setup lang="ts">
  import { toRefs } from 'vue'
  import type { LocationQuery } from 'vue-router'

  import type { IPagination, TPaginationPayload } from '@/types/api'
  import type { IOauth2ClientsPayload } from '@/types/oauth'
  import type { TWorkoutsPayload } from '@/types/workouts'
  import { rangePagination } from '@/utils/api'

  interface Props {
    pagination: IPagination
    path: string
    query: TWorkoutsPayload | TPaginationPayload | IOauth2ClientsPayload
  }
  const props = defineProps<Props>()
  const { pagination, path, query } = toRefs(props)

  function getQuery(page: number, cursor?: number): LocationQuery {
    const newQuery = Object.assign({}, query.value)
    newQuery.page = cursor ? page + cursor : page
    return newQuery as LocationQuery
  }
</script>

<style lang="scss" scoped>
  @use '~@/scss/vars.scss' as *;

  .pagination-center {
    display: flex;
    justify-content: center;
    font-size: 0.9em;

    a {
      text-decoration: none;
    }

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
      }
      .page-disabled-link {
        color: var(--disabled-color);
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
