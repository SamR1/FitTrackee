<template>
  <nav class="pagination-center" aria-label="navigation">
    <ul class="pagination">
      <li class="page-prev" :class="{ disabled: !pagination.has_prev }">
        <router-link
          v-slot="{ navigate }"
          class="page-link"
          :to="{ path, query: getQuery(pagination.page, -1) }"
          :disabled="!pagination.has_prev"
          :tabindex="pagination.has_prev ? 0 : -1"
        >
          <slot @click="pagination.has_next ? navigate : null">
            {{ $t('api.PAGINATION.PREVIOUS') }}
            <i class="fa fa-chevron-left" aria-hidden="true" />
          </slot>
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
          v-slot="{ navigate }"
          class="page-link"
          :to="{ path, query: getQuery(pagination.page, 1) }"
          :disabled="!pagination.has_next"
          :tabindex="pagination.has_next ? 0 : -1"
        >
          <slot @click="pagination.has_next ? navigate : null">
            {{ $t('api.PAGINATION.NEXT') }}
            <i class="fa fa-chevron-right" aria-hidden="true" />
          </slot>
        </router-link>
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
  @import '~@/scss/vars.scss';

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
            cursor: default;
            pointer-events: none;
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
